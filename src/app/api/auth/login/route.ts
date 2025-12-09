import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const body = await request.json();
  
  // You can change 'admin123' to any password you want
  const CORRECT_PASSWORD = process.env.ADMIN_PASSWORD || "admin123";

  if (body.password === CORRECT_PASSWORD) {
    // Set a cookie that lasts 24 hours
    const cookieStore = await cookies();
    cookieStore.set("admin_token", "secure_access_granted", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24, // 1 day
      path: "/",
    });
    
    return NextResponse.json({ success: true });
  }

  return NextResponse.json({ success: false }, { status: 401 });
}