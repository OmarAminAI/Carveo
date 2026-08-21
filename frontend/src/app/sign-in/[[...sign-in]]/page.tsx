import { SignIn } from "@clerk/nextjs";
import { AuthPageShell } from "@/components/auth-page-shell";

export default function SignInPage() {
  return (
    <AuthPageShell eyebrow="Welcome back" title="Continue your search.">
      <SignIn />
    </AuthPageShell>
  );
}
