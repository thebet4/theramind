import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  Brain,
  Clock,
  FileText,
  Heart,
  Mic,
  Shield,
  Users,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import Footer from "./Footer";
import Header from "./Header";

// Static waveform data for visualization
const waveformData = [
  { height: 45, opacity: 0.7 },
  { height: 62, opacity: 0.8 },
  { height: 38, opacity: 0.6 },
  { height: 71, opacity: 0.9 },
  { height: 55, opacity: 0.75 },
  { height: 42, opacity: 0.65 },
  { height: 68, opacity: 0.85 },
  { height: 51, opacity: 0.7 },
  { height: 76, opacity: 0.95 },
  { height: 44, opacity: 0.68 },
  { height: 59, opacity: 0.78 },
  { height: 47, opacity: 0.72 },
  { height: 64, opacity: 0.82 },
  { height: 39, opacity: 0.62 },
  { height: 72, opacity: 0.88 },
  { height: 53, opacity: 0.73 },
  { height: 41, opacity: 0.64 },
  { height: 67, opacity: 0.84 },
  { height: 58, opacity: 0.77 },
  { height: 48, opacity: 0.71 },
  { height: 73, opacity: 0.9 },
  { height: 46, opacity: 0.69 },
  { height: 61, opacity: 0.79 },
  { height: 52, opacity: 0.74 },
  { height: 69, opacity: 0.86 },
  { height: 43, opacity: 0.67 },
  { height: 56, opacity: 0.76 },
  { height: 49, opacity: 0.72 },
  { height: 65, opacity: 0.83 },
  { height: 54, opacity: 0.74 },
  { height: 70, opacity: 0.87 },
  { height: 40, opacity: 0.63 },
  { height: 63, opacity: 0.81 },
  { height: 50, opacity: 0.73 },
  { height: 74, opacity: 0.91 },
  { height: 57, opacity: 0.77 },
  { height: 66, opacity: 0.84 },
  { height: 45, opacity: 0.7 },
  { height: 60, opacity: 0.8 },
  { height: 48, opacity: 0.71 },
];

export default function LandingPage() {
  const { t } = useTranslation("translation", { keyPrefix: "landing" });

  return (
    <div className="min-h-screen">
      <Header />

      {/* Hero Section */}
      <section
        id="hero"
        className="relative overflow-hidden bg-gradient-to-b from-indigo-100 to-gray-50 pt-24 pb-20"
      >
        <div className="relative container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 lg:grid-cols-2">
            {/* Left Column - Content */}
            <div className="pt-8">
              <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 lg:text-6xl">
                {t("hero.title")}{" "}
                <span className="text-indigo-600">{t("hero.titleHighlight")}</span>{" "}
              </h1>

              <p className="mb-8 max-w-xl text-lg text-gray-600">{t("hero.subtitle")}</p>

              <div className="mb-12 flex flex-col gap-4 sm:flex-row">
                <Button size="lg">{t("hero.cta")}</Button>
              </div>

              {/* Feature Badges */}
              <div className="flex flex-wrap gap-6">
                <div className="flex items-center gap-2">
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-green-100">
                    <Shield className="h-3 w-3 text-green-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {t("hero.badges.confidential")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100">
                    <Clock className="h-3 w-3 text-blue-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {t("hero.badges.available")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-purple-100">
                    <Heart className="h-3 w-3 text-purple-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {t("hero.badges.evidenceBased")}
                  </span>
                </div>
              </div>
            </div>

            {/* Right Column - Audio Recorder Mockup */}
            <div className="relative">
              <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white p-8 shadow-2xl">
                {/* Session Info */}
                <div className="mb-8 text-center">
                  <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2">
                    <div className="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
                    <span className="text-sm font-medium text-indigo-900">
                      {t("hero.recorder.status")}
                    </span>
                  </div>
                  <h3 className="mb-2 text-xl font-semibold text-gray-900">
                    {t("hero.recorder.title")}
                  </h3>
                  <p className="text-sm text-gray-600">{t("hero.recorder.subtitle")}</p>
                </div>

                {/* Waveform Visualization */}
                <div className="relative mb-8 flex h-32 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 px-6">
                  <div className="flex h-full items-center gap-1 py-8">
                    {waveformData.map((wave, i) => (
                      <motion.div
                        key={i}
                        className="w-1 origin-bottom rounded-full"
                        style={{
                          height: `${wave.height}%`,
                          background:
                            "linear-gradient(to top, rgb(79, 70, 229), rgb(147, 51, 234))",
                          willChange: "transform, opacity",
                        }}
                        initial={{ scaleY: 1, opacity: wave.opacity }}
                        animate={{
                          scaleY: [1, 0.85, 0.65, 0.85, 1, 1.08, 1],
                          opacity: [
                            wave.opacity,
                            wave.opacity * 0.9,
                            wave.opacity * 0.75,
                            wave.opacity * 0.9,
                            wave.opacity,
                            wave.opacity,
                            wave.opacity,
                          ],
                        }}
                        transition={{
                          duration: 4,
                          repeat: Infinity,
                          delay: i * 0.04,
                          ease: "easeInOut",
                          times: [0, 0.2, 0.4, 0.6, 0.75, 0.9, 1],
                        }}
                      />
                    ))}
                  </div>
                </div>

                {/* Timer */}
                <div className="mb-8 text-center">
                  <div className="mb-1 text-4xl font-bold text-gray-900">12:34</div>
                  <div className="text-sm text-gray-500">{t("hero.recorder.duration")}</div>
                </div>

                {/* Control Buttons */}
                <div className="mb-6 flex items-center justify-center gap-4">
                  <button className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 transition-colors hover:bg-gray-200">
                    <svg
                      className="h-5 w-5 text-gray-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>

                  <button className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 shadow-lg transition-all hover:from-indigo-700 hover:to-purple-700">
                    <div className="h-6 w-6 rounded bg-white"></div>
                  </button>

                  <button className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 transition-colors hover:bg-gray-200">
                    <svg
                      className="h-5 w-5 text-gray-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </button>
                </div>

                {/* Security Info */}
                <div className="flex items-center justify-center gap-6 border-t border-gray-100 pt-6">
                  <div className="flex items-center gap-1.5 text-xs text-gray-500">
                    <Shield className="h-3.5 w-3.5" />
                    <span>{t("hero.recorder.encrypted")}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-gray-500">
                    <Mic className="h-3.5 w-3.5" />
                    <span>{t("hero.recorder.quality")}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="scroll-mt-16 bg-gray-50 py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Clock,
                title: t("features.feature1.title"),
                description: t("features.feature1.description"),
              },
              {
                icon: Shield,
                title: t("features.feature2.title"),
                description: t("features.feature2.description"),
              },
              {
                icon: Brain,
                title: t("features.feature3.title"),
                description: t("features.feature3.description"),
              },
              {
                icon: BarChart3,
                title: t("features.feature4.title"),
                description: t("features.feature4.description"),
              },
              {
                icon: Heart,
                title: t("features.feature5.title"),
                description: t("features.feature5.description"),
              },
              {
                icon: Users,
                title: t("features.feature6.title"),
                description: t("features.feature6.description"),
              },
            ].map((feature, index) => (
              <Card
                key={index}
                className="border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="space-y-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600">
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
                    <p className="text-sm leading-relaxed text-gray-600">{feature.description}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="scroll-mt-16 bg-gray-50 py-20">
        <span id="about" className="absolute -mt-16"></span>
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto mb-16 max-w-3xl text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">
              {t("benefits.sectionTitle")}
            </h2>
          </div>

          <div className="mx-auto max-w-5xl">
            <div className="grid grid-cols-1 gap-12 md:grid-cols-3">
              {[
                {
                  step: "01",
                  icon: Mic,
                  title: t("benefits.step1.title"),
                  description: t("benefits.step1.description"),
                },
                {
                  step: "02",
                  icon: Brain,
                  title: t("benefits.step2.title"),
                  description: t("benefits.step2.description"),
                },
                {
                  step: "03",
                  icon: FileText,
                  title: t("benefits.step3.title"),
                  description: t("benefits.step3.description"),
                },
              ].map((step, index) => (
                <div key={index} className="relative">
                  <div className="mb-4 text-6xl font-bold text-indigo-100">{step.step}</div>
                  <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-purple-600">
                    <step.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="mb-3 text-xl font-semibold text-gray-900">{step.title}</h3>
                  <p className="text-gray-600">{step.description}</p>

                  {index < 2 && (
                    <div className="absolute top-20 -right-6 hidden h-8 w-8 md:block">
                      <ArrowRight className="h-8 w-8 text-indigo-200" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section
        id="pricing"
        className="scroll-mt-16 bg-gradient-to-r from-indigo-600 to-purple-600 py-20 text-white"
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">{t("cta.title")}</h2>
            <p className="mb-8 text-lg text-white/90">{t("cta.subtitle")}</p>
            <Button
              size="xl"
              variant="outline"
              className="mb-4 bg-white text-indigo-600 hover:bg-gray-100"
            >
              {t("cta.button")}
              <ArrowRight className="ml-2" />
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
