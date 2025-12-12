"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch"; // Ensure you have a switch component or use a button
import { Lock, Unlock } from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
  const [isLocked, setIsLocked] = useState(false);
  const [loading, setLoading] = useState(true);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/settings/vendor-lock`);
      const data = await res.json();
      setIsLocked(data.locked);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleLock = async () => {
    const newState = !isLocked;
    try {
      await fetch(`${apiUrl}/api/settings/vendor-lock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locked: newState })
      });
      setIsLocked(newState);
    } catch (e) {
      alert("Failed to update setting");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900">System Settings</h1>
            <Link href="/"><Button variant="outline">Back to Dashboard</Button></Link>
        </header>

        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    {isLocked ? <Lock className="text-red-500" /> : <Unlock className="text-green-500" />}
                    Vendor Registration Status
                </CardTitle>
                <CardDescription>
                    Control whether new vendors can sign up on the bot.
                </CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
                <div>
                    <h3 className="font-semibold text-lg">
                        {isLocked ? "⛔ Registration Locked" : "✅ Registration Open"}
                    </h3>
                    <p className="text-slate-500 text-sm">
                        {isLocked 
                            ? "New users cannot register as vendors. Existing vendors can still login." 
                            : "New users can freely register as vendors."}
                    </p>
                </div>
                
                <Button 
                    size="lg"
                    variant={isLocked ? "destructive" : "default"}
                    onClick={toggleLock}
                    disabled={loading}
                    className={isLocked ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}
                >
                    {isLocked ? "Unlock Registration" : "Lock Registration"}
                </Button>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}