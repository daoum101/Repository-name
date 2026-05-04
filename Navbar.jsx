import { Link, useLocation } from "react-router-dom";
import { Sparkles } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

export default function Navbar({ compact = false }) {
  const { pathname } = useLocation();
  return (
    <header
      data-testid="navbar"
      className="sticky top-0 z-40 backdrop-blur-xl bg-background/70 border-b border-border/60"
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" data-testid="navbar-logo" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-medium tracking-tight">
            AutoSite<span className="text-primary">.</span>AI
            <span className="ml-1 label-mono text-[9px]">PRO</span>
          </span>
        </Link>
        {!compact && (
          <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            <a href="/#features" className="hover:text-foreground transition-colors" data-testid="nav-features">Fonctionnalités</a>
            <a href="/#templates" className="hover:text-foreground transition-colors" data-testid="nav-templates">Templates</a>
            <a href="/#how" className="hover:text-foreground transition-colors" data-testid="nav-how">Process</a>
          </nav>
        )}
        <div className="flex items-center gap-3">
          <ThemeToggle />
          {pathname === "/" ? (
            <Link
              to="/dashboard"
              data-testid="nav-cta"
              className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium btn-glow"
            >
              Ouvrir le studio
            </Link>
          ) : (
            <Link
              to="/new"
              data-testid="nav-cta"
              className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium btn-glow"
            >
              + Nouveau projet
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
