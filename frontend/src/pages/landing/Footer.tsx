import { Brain } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function Footer() {
  const { t } = useTranslation("translation", { keyPrefix: "landing.footer" });

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">TheraMind</span>
            </div>
            <p className="max-w-xs text-sm text-gray-400">{t("tagline")}</p>
          </div>

          {/* Product Column */}
          <div>
            <h3 className="mb-4 font-semibold text-white">{t("product")}</h3>
            <ul className="space-y-3">
              <li>
                <a
                  href="#features"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("features")}
                </a>
              </li>
              <li>
                <a href="#faq" className="text-sm text-gray-400 transition-colors hover:text-white">
                  {t("faq")}
                </a>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h3 className="mb-4 font-semibold text-white">{t("company")}</h3>
            <ul className="space-y-3">
              <li>
                <a
                  href="#about"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("about")}
                </a>
              </li>
              <li>
                <a
                  href="#blog"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("blog")}
                </a>
              </li>
              <li>
                <a
                  href="#careers"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("careers")}
                </a>
              </li>
              <li>
                <a
                  href="#contact"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("contact")}
                </a>
              </li>
            </ul>
          </div>

          {/* Legal Column */}
          <div>
            <h3 className="mb-4 font-semibold text-white">{t("legal")}</h3>
            <ul className="space-y-3">
              <li>
                <a
                  href="#privacy"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("privacy")}
                </a>
              </li>
              <li>
                <a
                  href="#terms"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("terms")}
                </a>
              </li>
              <li>
                <a
                  href="#hipaa"
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {t("hipaa")}
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 border-t border-gray-800 pt-8">
          <p className="text-center text-sm text-gray-400">{t("rights")}</p>
        </div>
      </div>
    </footer>
  );
}
