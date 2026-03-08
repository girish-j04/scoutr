import { ClubProvider } from "@/lib/ClubContext";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <ClubProvider>{children}</ClubProvider>;
}
