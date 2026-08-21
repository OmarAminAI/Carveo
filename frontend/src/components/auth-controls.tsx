"use client";

import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import { cn } from "@/lib/utils";

type AuthControlsProps = {
  mobile?: boolean;
};

export function AuthControls({ mobile = false }: AuthControlsProps) {
  return (
    <>
      <Show when="signed-out">
        <div className={cn("items-center gap-2", mobile ? "mt-8 grid" : "hidden md:flex")}>
          <SignInButton mode="redirect">
            <button
              type="button"
              className={cn(
                "h-9 border border-white/25 px-4 text-sm font-medium text-white transition-colors hover:border-white hover:bg-white/10",
                mobile && "w-full",
              )}
            >
              Sign in
            </button>
          </SignInButton>
          <SignUpButton mode="redirect">
            <button
              type="button"
              className={cn(
                "h-9 bg-signal px-4 text-sm font-semibold text-obsidian transition-colors hover:bg-white",
                mobile && "w-full",
              )}
            >
              Create account
            </button>
          </SignUpButton>
        </div>
      </Show>
      <Show when="signed-in">
        <div className={cn("items-center", mobile ? "mt-8 flex" : "hidden md:flex")}>
          <UserButton
            appearance={{ elements: { avatarBox: "size-9 rounded-sm" } }}
            userProfileMode="modal"
          />
        </div>
      </Show>
    </>
  );
}
