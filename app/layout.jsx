import "./globals.css";

export const metadata = {
  title: "VideoMind : AI Powered Video Intelligence Platform",
  description: "Analyze videos, extract insights, and chat with content",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
