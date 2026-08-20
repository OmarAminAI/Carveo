import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex h-10 shrink-0 items-center justify-center gap-2 border px-4 text-sm font-semibold transition-[transform,color,background-color,border-color] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        default: "border-primary bg-primary text-primary-foreground hover:bg-graphite",
        signal: "border-accent bg-accent text-accent-foreground hover:bg-[#eeb400]",
        outline: "border-border bg-transparent text-foreground hover:bg-secondary",
        ghost: "border-transparent bg-transparent text-current hover:bg-white/10",
      },
      size: { default: "h-10 px-4", sm: "h-8 px-3 text-xs", icon: "size-10 p-0" },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>;

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

export { buttonVariants };
