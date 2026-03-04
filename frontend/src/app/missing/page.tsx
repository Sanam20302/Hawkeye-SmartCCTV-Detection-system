"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Trash2, UserPlus, UserSearch } from "lucide-react";
import { MissingFace } from "@/types";

const API_URL = "http://localhost:8000";

export default function MissingPersonsPage() {
    const [missingFaces, setMissingFaces] = useState<MissingFace[]>([]);
    const [uploading, setUploading] = useState(false);
    const [newName, setNewName] = useState("");
    const [category, setCategory] = useState("Missing");

    const fetchFaces = async () => {
        try {
            const missingRes = await fetch(`${API_URL}/missing`);

            if (missingRes.ok) setMissingFaces(await missingRes.json());
        } catch (e) {
            console.error("Failed to fetch faces", e);
        }
    };

    useEffect(() => {
        fetchFaces();
    }, []);

    const handleAddFace = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        setUploading(true);

        try {
            const res = await fetch(`${API_URL}/missing`, {
                method: "POST",
                body: formData,
            });
            if (res.ok) {
                setNewName("");
                setCategory("Missing");
                // Reset form
                (e.target as HTMLFormElement).reset();
                fetchFaces();
            }
        } catch (error) {
            console.error("Upload error", error);
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Remove this person from missing/wanted list?")) return;
        try {
            await fetch(`${API_URL}/missing/${id}`, { method: "DELETE" });
            fetchFaces();
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Missing/Wanted Persons</h2>
            </div>

            <div className="grid gap-6">
                {/* Missing Faces Section */}
                <Card className="border-destructive/20 bg-destructive/5">
                    <CardHeader>
                        <CardTitle className="flex items-center text-destructive">
                            <UserSearch className="mr-2 h-5 w-5" /> Active Search Targets
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {/* Upload Form */}
                        <form onSubmit={handleAddFace} className="flex gap-4 mb-6 p-4 border border-dashed border-destructive/30 rounded-lg bg-destructive/5 items-end flex-wrap">
                            <div className="flex-1 min-w-[200px]">
                                <label className="block text-xs font-mono text-destructive mb-1">NAME / ALIAS</label>
                                <input
                                    name="name"
                                    required
                                    className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm text-white focus:border-destructive outline-none"
                                    placeholder="Person Name"
                                    value={newName}
                                    onChange={(e) => setNewName(e.target.value)}
                                />
                            </div>

                            <div className="flex-1 min-w-[150px]">
                                <label className="block text-xs font-mono text-destructive mb-1">CATEGORY</label>
                                <select
                                    name="category"
                                    value={category}
                                    onChange={(e) => setCategory(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm text-white focus:border-destructive outline-none"
                                >
                                    <option value="Missing">Missing</option>
                                    <option value="Wanted">Wanted</option>
                                </select>
                            </div>

                            <div className="flex-1 min-w-[200px]">
                                <label className="block text-xs font-mono text-destructive mb-1">PHOTO</label>
                                <input
                                    name="file"
                                    type="file"
                                    required
                                    accept="image/*"
                                    className="block w-full text-sm text-slate-500
                                  file:mr-4 file:py-2 file:px-4
                                  file:rounded-full file:border-0
                                  file:text-xs file:font-semibold
                                  file:bg-destructive file:text-white
                                  hover:file:bg-destructive/80
                            "
                                />
                            </div>
                            <div className="flex h-[38px]">
                                <Button type="submit" disabled={uploading} size="sm" variant="destructive" className="h-full">
                                    {uploading ? "..." : <UserPlus className="h-4 w-4" />}
                                </Button>
                            </div>
                        </form>

                        {/* List */}
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                            {missingFaces.map((face) => (
                                <div key={face.id} className="relative group overflow-hidden rounded-lg border border-destructive/50 bg-zinc-900">
                                    {/* eslint-disable-next-line @next/next/no-img-element */}
                                    <img
                                        src={`${API_URL}/missing_faces/${face.image_path.split(/[/\\]/).pop()}`}
                                        alt={face.name}
                                        className="w-full h-40 object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                                    />
                                    <div className="absolute bottom-0 left-0 right-0 bg-black/80 p-2 flex justify-between items-center border-t border-destructive/30">
                                        <span className="text-xs font-bold text-white truncate pr-2">{face.name}</span>
                                        <button onClick={() => handleDelete(face.id)} className="text-zinc-500 hover:text-red-400">
                                            <Trash2 className="h-3 w-3" />
                                        </button>
                                    </div>
                                    <div className={`absolute top-2 right-2 text-white text-[10px] px-2 py-0.5 rounded-full font-mono font-bold shadow-sm ${face.category === 'Wanted' ? 'bg-destructive' : 'bg-orange-500'}`}>
                                        {face.category ? face.category.toUpperCase() : 'MISSING'}
                                    </div>
                                </div>
                            ))}
                            {missingFaces.length === 0 && (
                                <div className="col-span-full text-center text-muted-foreground text-sm py-8">
                                    No missing or wanted persons currently listed.
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
