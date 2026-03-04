import cv2
import numpy as np
import torch
from PIL import Image
import os
import uuid
from backend import database

# --- Colors ---
MAROON = (0, 0, 128)      
RED_ALERT = (0, 0, 255)  
ZONE_COLOR = (0, 0, 255)  
GREEN_SAFE = (0, 255, 0)

def check_trespassing(bbox, zone_coords):
    x1, y1, x2, y2 = bbox
    # Check if the "feet" are in the zone
    foot_x, foot_y = int((x1 + x2) / 2), int(y2)
    zx1, zy1, zx2, zy2 = zone_coords
    
    # Normalize coordinates to handle arbitrary corner order
    min_x, max_x = min(zx1, zx2), max(zx1, zx2)
    min_y, max_y = min(zy1, zy2), max(zy1, zy2)
    
    return min_x < foot_x < max_x and min_y < foot_y < max_y

def check_loitering(track_id, center_point, track_history, current_time, threshold):
    if track_id not in track_history:
        track_history[track_id].append((current_time, center_point))
        return False
    
    first_time = track_history[track_id][0][0]
    duration = current_time - first_time
    track_history[track_id].append((current_time, center_point))

    if duration > threshold:
        return True
    return False

def recognize_frame_faces(frame, tracks, mtcnn, resnet, known_faces, device, saved_untrusted=None, missing_faces=None):
    """
    frame: cv2 image (BGR)
    tracks: deepsort tracks
    known_faces: list of {name, embedding}
    missing_faces: list of {name, embedding}
    """
    if saved_untrusted is None:
        saved_untrusted = set()
    if missing_faces is None:
        missing_faces = []

    if mtcnn is None or resnet is None:
        return [], saved_untrusted
        
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)
    frame_h, frame_w = frame.shape[:2]
    
    results = []

    for track in tracks:
        if not track.is_confirmed() or track.time_since_update > 1:
            continue
            
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
        
        # Clamp coordinates
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame_w, x2), min(frame_h, y2)
        
        if x2 <= x1 or y2 <= y1:
            continue

        person_crop = pil_img.crop((x1, y1, x2, y2))
        
        # Detect face in person crop
        try:
            boxes, _ = mtcnn.detect(person_crop)
        except (ValueError, RuntimeError, IndexError):
            continue
        except Exception as e:
            print(f"Unexpected error in face detection: {e}")
            continue
        
        if boxes is not None:
            for box in boxes:
                fx1, fy1, fx2, fy2 = box
                
                # Check face resolution
                if (fx2-fx1) < 20 or (fy2-fy1) < 20: 
                    continue
                
                # Manual crop for embedding
                face_crop_pil = person_crop.crop((fx1, fy1, fx2, fy2))
                
                try:
                    face_tensor = torch.from_numpy(np.array(face_crop_pil.resize((160, 160)))).permute(2, 0, 1).float()
                    face_tensor = (face_tensor - 127.5) / 128.0 # Standard normalization for facenet
                    face_tensor = face_tensor.unsqueeze(0).to(device)
                    
                    with torch.no_grad():
                        embedding = resnet(face_tensor).detach().cpu().numpy()[0]
                    
                    # Compare with known faces
                    name = "Unknown"
                    is_trusted = False
                    is_missing = False
                    min_dist = 0.8 # Threshold
                    
                    # Check missing faces first
                    for mf in missing_faces:
                        missing_emb = np.array(mf['embedding'])
                        dist = np.linalg.norm(embedding - missing_emb)
                        if dist < min_dist:
                            min_dist = dist
                            name = mf['name']
                            is_missing = True
                            is_missing_category = mf.get('category', 'Missing')
                    
                    # If not missing, check trusted faces
                    if not is_missing:
                        for kf in known_faces:
                            known_emb = np.array(kf['embedding'])
                            dist = np.linalg.norm(embedding - known_emb)
                            if dist < min_dist:
                                min_dist = dist
                                name = kf['name']
                                is_trusted = True
                    
                    # Store result relative to full frame
                    abs_fx1 = int(x1 + fx1)
                    abs_fy1 = int(y1 + fy1)
                    abs_fx2 = int(x1 + fx2)
                    abs_fy2 = int(y1 + fy2)
                    
                    results.append({
                        "box": (abs_fx1, abs_fy1, abs_fx2, abs_fy2),
                        "name": name,
                        "trusted": is_trusted,
                        "missing": is_missing,
                        "category": is_missing_category if is_missing else None
                    })

                    # Handle Untrusted Capture
                    if not is_trusted and not is_missing:
                        if track.track_id not in saved_untrusted:
                            filename = f"capture_{uuid.uuid4().hex}.jpg"
                            fpath = os.path.join("backend/captured_faces", filename)
                            save_img = cv2.cvtColor(np.array(face_crop_pil), cv2.COLOR_RGB2BGR)
                            cv2.imwrite(fpath, save_img)
                            database.log_untrusted_face(filename)
                            saved_untrusted.add(track.track_id)

                except Exception as e:
                    print(f"Face processing error: {e}")
                    pass

    return results, saved_untrusted

def process_frame_annotations(frame, tracks, current_time, track_history, loitering_saved, settings, 
                              mtcnn=None, resnet=None, known_faces=None, device='cpu', saved_untrusted_session=None, missing_faces=None):
    
    annotated_frame = frame.copy()
    
    # Initialize saved_untrusted_session if None
    if saved_untrusted_session is None:
        saved_untrusted_session = set()

    # 1. Draw Restricted Zone
    if settings['trespassing_enabled']:
        tz = settings['trespassing_zone']
        # Normalize for drawing
        x_min, x_max = min(tz[0], tz[2]), max(tz[0], tz[2])
        y_min, y_max = min(tz[1], tz[3]), max(tz[1], tz[3])
        
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), ZONE_COLOR, -1)
        
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0, annotated_frame)
        
        cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), MAROON, 2)
        cv2.putText(annotated_frame, "Restricted Zone", (x_min, y_min-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, MAROON, 2)

    frame_alerts = {
        'count': 0,
        'trespassing': False,
        'loitering': False,
        'crowd': False,
        'untrusted_face': False,
        'missing_person': False,
        'missing_person_name': '',
        'missing_person_category': ''
    }

    # Run Face Recognition if models provided
    face_results = []
    if mtcnn and resnet:
        face_results, saved_untrusted_session = recognize_frame_faces(
            frame, tracks, mtcnn, resnet, known_faces, device, saved_untrusted_session, missing_faces
        )
        # Check if any face is untrusted or missing
        for res in face_results:
            if res.get('missing', False):
                frame_alerts['missing_person'] = True
                frame_alerts['missing_person_name'] = res['name']
                frame_alerts['missing_person_category'] = res.get('category', 'Missing')
            elif not res['trusted']:
                frame_alerts['untrusted_face'] = True

    for track in tracks:
        if not track.is_confirmed() and track.time_since_update > 1:
            continue
        
        frame_alerts['count'] += 1
        track_id = track.track_id
        
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
        bbox = (x1, y1, x2, y2)
        center = (int((x1+x2)/2), int((y1+y2)/2))

        # Check Trespassing
        if settings['trespassing_enabled'] and check_trespassing(bbox, settings['trespassing_zone']):
            frame_alerts['trespassing'] = True

        # Check Loitering
        if settings['loitering_enabled']:
            if check_loitering(track_id, center, track_history, current_time, settings['loitering_threshold']):
                frame_alerts['loitering'] = True
                loitering_saved[track_id] = True
    
    # Check crowd
    if settings['crowd_enabled'] and frame_alerts['count'] > settings['crowd_threshold']:
        frame_alerts['crowd'] = True


    # Draw Stats
    y_pos = 20
    cv2.putText(annotated_frame, f"People Count: {frame_alerts['count']}", (10, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, MAROON, 2)
    
    if frame_alerts['crowd']:
        y_pos += 20
        cv2.putText(annotated_frame, "Crowd Alert!", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_ALERT, 2)

    if frame_alerts['loitering']:
        y_pos += 20
        cv2.putText(annotated_frame, "Loitering Alert!", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_ALERT, 2)

    if frame_alerts['trespassing']:
        y_pos += 20
        cv2.putText(annotated_frame, "Trespassing Alert!", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_ALERT, 2)
    
    if frame_alerts['missing_person']:
        y_pos += 20
        cat = frame_alerts['missing_person_category'].upper()
        cv2.putText(annotated_frame, f"{cat} DETECTED: {frame_alerts['missing_person_name']}", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_ALERT if cat == 'WANTED' else (0, 165, 255), 2)
    
    # Draw Faces
    for res in face_results:
        fx1, fy1, fx2, fy2 = res['box']
        if res.get('missing', False):
            cat = res.get('category', 'Missing').upper()
            color = RED_ALERT if cat == 'WANTED' else (0, 165, 255) # Orange for Missing, Red for Wanted
            label = f"{cat}: {res['name']}"
        elif res['trusted']:
            color = GREEN_SAFE
            label = res['name']
        else:
            color = RED_ALERT
            label = res['name']
            
        cv2.rectangle(annotated_frame, (fx1, fy1), (fx2, fy2), color, 2)
        cv2.putText(annotated_frame, label, (fx1, fy1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return annotated_frame, frame_alerts, saved_untrusted_session
