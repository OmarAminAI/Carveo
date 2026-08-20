import { AppFooter } from "@/components/app-footer";
import { AppHeader } from "@/components/app-header";

export const dynamic = "force-dynamic";
import { ProfileProvider } from "@/profile/profile-provider";

export default function LocaleLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <ProfileProvider><AppHeader />{children}<AppFooter /></ProfileProvider>;
}
