// import type { NextRequest } from "next/server";
// import { auth0 } from "./lib/auth0";

// export async function middleware(request: NextRequest) {
//   return await auth0.middleware(request);
// }

// export const config = {
//   matcher: [
//     "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
//   ],
// };

import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { auth0 } from "./lib/auth0";

export async function middleware(request: NextRequest) {
  try {
    return await auth0.middleware(request);
  } catch (error) {
    console.error("Auth0 middleware error:", error);

    // Redirect to login on error
    const loginUrl = new URL("/api/auth/login", request.url);
    return NextResponse.redirect(loginUrl);
  }
}

export const config = {
  matcher: [
    "/((?!api/auth|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
