import "./globals.css";

export const metadata = {
  title: "Orbital Launch Tracker",
  description: "Track historic orbital launch attempts"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
