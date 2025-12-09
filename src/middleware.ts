import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Check for the admin cookie
  const token = request.cookies.get("admin_token");
  
  // If user is trying to access login page, let them
  if (request.nextUrl.pathname === "/login") {
    if (token) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // If user has no token and tries to access dashboard, kick them to login
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

// Protect these paths
export const config = {
  matcher: [
    "/",
    "/vendors/:path*",
    "/promotions/:path*",
    "/subscribers/:path*",
    "/payments/:path*",
    "/support/:path*",
    "/verifications/:path*",
    "/broadcasts/:path*",
  ],
};