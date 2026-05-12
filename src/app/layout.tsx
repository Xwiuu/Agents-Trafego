'use client';

import './globals.css';
import { Footer } from './components/Footer';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="bg-zinc-950 min-h-screen flex flex-col">
        {children}
        <Footer />
      </body>
    </html>
  );
}
