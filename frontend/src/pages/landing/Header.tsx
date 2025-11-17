import { Button } from "@/components/ui/button";
import { Brain, Menu } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const { t } = useTranslation("translation", { keyPrefix: "landing.header" });

  const handleSmoothScroll = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    const element = document.querySelector(targetId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
      setMobileMenuOpen(false); // Close mobile menu after clicking
    }
  };

  return (
    <header className="fixed top-0 right-0 left-0 z-50 border-b border-gray-200 bg-white">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <a href="#hero" onClick={(e) => handleSmoothScroll(e, "#hero")}>
            <div className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">TheraMind</span>
            </div>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden items-center gap-8 md:flex">
            <a
              href="#features"
              onClick={(e) => handleSmoothScroll(e, "#features")}
              className="text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
            >
              {t("features")}
            </a>
            <a
              href="#how-it-works"
              onClick={(e) => handleSmoothScroll(e, "#how-it-works")}
              className="text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
            >
              {t("howItWorks")}
            </a>
            <a
              href="#about"
              onClick={(e) => handleSmoothScroll(e, "#about")}
              className="text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
            >
              {t("about")}
            </a>
          </div>

          {/* Desktop CTA Buttons */}
          <div className="hidden items-center gap-3 md:flex">
            <Button
              variant="default"
              size="default"
              className="bg-indigo-600 text-white hover:bg-indigo-700"
            >
              {t("getStarted")}
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="rounded-md p-2 transition-colors hover:bg-gray-100 md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="border-t border-gray-200 py-4 md:hidden">
            <div className="flex flex-col gap-4">
              <a
                href="#features"
                onClick={(e) => handleSmoothScroll(e, "#features")}
                className="py-2 text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
              >
                {t("features")}
              </a>
              <a
                href="#how-it-works"
                onClick={(e) => handleSmoothScroll(e, "#how-it-works")}
                className="py-2 text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
              >
                {t("howItWorks")}
              </a>
              <a
                href="#about"
                onClick={(e) => handleSmoothScroll(e, "#about")}
                className="py-2 text-sm font-medium text-gray-700 transition-colors hover:text-gray-900"
              >
                {t("about")}
              </a>
              <div className="flex flex-col gap-2 border-t border-gray-200 pt-4">
                <Button
                  size="default"
                  className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                >
                  {t("getStarted")}
                </Button>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
