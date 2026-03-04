export interface Settings {
    loitering_threshold: number;
    crowd_threshold: number;
    confidence_threshold: number;
    trespassing_zone: [number, number, number, number];
    trespassing_enabled: boolean;
    loitering_enabled: boolean;
    crowd_enabled: boolean;
}

export interface TrustedFace {
    id: number;
    name: string;
    embedding: number[];
    image_path: string;
}

export interface MissingFace {
    id: number;
    name: string;
    embedding: number[];
    image_path: string;
    category?: string;
}

export interface UntrustedFace {
    id: number;
    image_path: string;
    timestamp: string;
}

export interface APIResponse {
    message: string;
}
