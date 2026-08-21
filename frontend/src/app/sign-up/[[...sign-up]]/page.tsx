import { SignUp } from "@clerk/nextjs";
import { AuthPageShell } from "@/components/auth-page-shell";

export default function SignUpPage() {
  return (
    <AuthPageShell eyebrow="Your buyer workspace" title="Make every search count.">
      <SignUp />
    </AuthPageShell>
  );
}
