import { AppFooter } from "@/components/app-footer";
import { AppHeader } from "@/components/app-header";
import { ProfileProvider } from "@/profile/profile-provider";

export default function LocaleLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <ProfileProvider><AppHeader />{children}<AppFooter /></ProfileProvider>;
}
