import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Sparkles, Zap, Download, Gauge, MapPin, Palette, Wand2,
  ArrowRight, Layers, Shield, Globe, ChevronRight,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { SECTORS } from "@/data/sectors";

const HERO_BG = "https://static.prod-images.emergentagent.com/jobs/e1c69fd1-6824-4f3d-9c96-8fe0d4476348/images/d3a8d787bc7707d1ffeced298372005045854f652ec2028c1e689e03d276221b.png";

const FEATURES = [
  { icon: Wand2, title: "Génération IA premium", desc: "Claude Sonnet 4.5 écrit un site complet, cohérent avec votre secteur.", span: "md:col-span-2" },
  { icon: Gauge, title: "Score SEO 100", desc: "Checklist claire, local business, schema.org intégré." },
  { icon: Palette, title: "Design agence", desc: "Typographie Clash Display, glassmorphism, layout asymétrique." },
  { icon: MapPin, title: "SEO local intégré", desc: "Ville dans titres, Maps, itinéraires, Google Business ready." },
  { icon: Download, title: "Export ZIP 1-clic", desc: "HTML + sitemap + robots. Deploy direct Netlify / Vercel / GitHub Pages." },
  { icon: Layers, title: "15 secteurs experts", desc: "Restaurant, garage, coach, immobilier, médecin… chaque secteur calibré.", span: "md:col-span-2" },
];

const STEPS = [
  { n: "01", title: "Brief intelligent", desc: "Vous répondez à un formulaire guidé — nom, ville, ton, couleurs." },
  { n: "02", title: "Génération IA", desc: "Claude Sonnet 4.5 rédige tout le site : copie marketing, FAQ, SEO, témoignages." },
  { n: "03", title: "Preview & édition", desc: "Aperçu desktop / tablet / mobile. Ajustez couleurs, nom, contenus." },
  { n: "04", title: "Export ZIP prêt à déployer", desc: "Téléchargez un site propre, SEO local, sans dépendance." },
];

export default function Landing() {
  return (
    <div className="dark">
      <Navbar />

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-60 pointer-events-none"
          style={{
            backgroundImage: `url(${HERO_BG})`,
            backgroundSize: "cover",
            backgroundPosition: "right center",
            maskImage: "linear-gradient(to left, black 30%, transparent 80%)",
            WebkitMaskImage: "linear-gradient(to left, black 30%, transparent 80%)",
          }}
        />
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-primary/25 blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-6 pt-24 pb-32">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9 }}>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-card text-xs label-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              Propulsé par Claude Sonnet 4.5
            </div>
          </motion.div>

          <div className="grid lg:grid-cols-12 gap-12 items-end mt-10">
            <motion.div
              initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.1 }}
              className="lg:col-span-8"
            >
              <h1 className="text-5xl sm:text-6xl lg:text-[6rem] font-medium leading-[0.95] tracking-tighter">
                Des sites web{" "}
                <span className="relative inline-block">
                  <span className="relative z-10 italic font-light">niveau agence</span>
                  <span className="absolute inset-x-0 bottom-2 h-3 bg-primary/40 -z-0 blur-sm" />
                </span>
                ,
                <br />
                générés par votre IA.
              </h1>
              <p className="mt-8 text-lg text-muted-foreground max-w-2xl leading-relaxed">
                AutoSite AI Pro transforme un brief en un site complet, SEO-optimisé et localement référencé. 
                Design premium, typographie soignée, export ZIP prêt à déployer — sans toucher une ligne de code.
              </p>
              <div className="mt-10 flex flex-wrap gap-3">
                <Link
                  to="/new"
                  data-testid="hero-cta-primary"
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-primary text-primary-foreground font-medium btn-glow"
                >
                  Créer mon premier site
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/dashboard"
                  data-testid="hero-cta-secondary"
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full border border-border bg-card/50 hover:bg-card transition-colors backdrop-blur-sm"
                >
                  Voir mes projets
                </Link>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.3 }}
              className="lg:col-span-4 grid gap-3"
            >
              {[
                { k: "15", v: "secteurs premium" },
                { k: "< 45s", v: "génération complète" },
                { k: "100", v: "score Lighthouse visé" },
              ].map((s) => (
                <div key={s.v} className="p-5 rounded-2xl border border-border bg-card/50 backdrop-blur-sm">
                  <div className="text-3xl font-medium text-primary">{s.k}</div>
                  <div className="label-mono mt-1">{s.v}</div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Trust row */}
          <div className="mt-24 flex items-center gap-6 text-xs text-muted-foreground flex-wrap">
            <span className="label-mono">— Stack</span>
            <span>Claude Sonnet 4.5</span>
            <span className="text-border">·</span>
            <span>Schema.org LocalBusiness</span>
            <span className="text-border">·</span>
            <span>Mobile-first</span>
            <span className="text-border">·</span>
            <span>Google Business ready</span>
          </div>
        </div>
      </section>

      {/* FEATURES BENTO */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-28 border-t border-border">
        <div className="flex flex-wrap items-end justify-between gap-8 mb-14">
          <div>
            <div className="label-mono mb-3">— Fonctionnalités</div>
            <h2 className="text-4xl sm:text-5xl font-medium max-w-2xl leading-tight">
              Tout ce qu'il faut pour vendre,<br />rien de ce qui encombre.
            </h2>
          </div>
          <p className="max-w-sm text-muted-foreground">
            Un studio compact qui couvre brief → design → SEO → export en un seul flux.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.6, delay: i * 0.05 }}
              className={`group relative p-8 rounded-2xl border border-border bg-card hover:border-primary/40 transition-all duration-500 ${f.span || ""}`}
              data-testid={`feature-${i}`}
            >
              <div className="w-10 h-10 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center mb-5">
                <f.icon className="w-4 h-4 text-primary" />
              </div>
              <h3 className="text-xl font-medium mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* TEMPLATES */}
      <section id="templates" className="max-w-7xl mx-auto px-6 py-28 border-t border-border">
        <div className="flex flex-wrap items-end justify-between gap-8 mb-14">
          <div>
            <div className="label-mono mb-3">— Templates premium</div>
            <h2 className="text-4xl sm:text-5xl font-medium max-w-2xl leading-tight">
              15 secteurs. Zéro template basique.
            </h2>
          </div>
          <Link to="/new" className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1" data-testid="templates-all-link">
            Voir tous les secteurs <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {SECTORS.slice(0, 6).map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="group relative overflow-hidden rounded-2xl border border-border bg-card"
              data-testid={`template-card-${s.id}`}
            >
              <div
                className="aspect-[4/3] w-full bg-cover bg-center transition-transform duration-700 group-hover:scale-105"
                style={{ backgroundImage: `url(${s.thumb})` }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
              <div className="absolute inset-x-0 bottom-0 p-6 flex items-end justify-between">
                <div>
                  <div className="label-mono" style={{ color: s.accent }}>— 0{i + 1}</div>
                  <div className="text-xl font-medium mt-1">{s.name}</div>
                </div>
                <Link to="/new" state={{ sector: s.id }} className="w-9 h-9 rounded-full bg-primary flex items-center justify-center hover:scale-110 transition-transform" data-testid={`template-use-${s.id}`}>
                  <ArrowRight className="w-4 h-4 text-white" />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-5 grid grid-cols-3 md:grid-cols-9 gap-2">
          {SECTORS.slice(6).map((s) => (
            <div key={s.id} className="px-3 py-2 rounded-full border border-border bg-card/50 text-xs text-center truncate" title={s.name}>
              {s.name.split(" / ")[0]}
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="max-w-7xl mx-auto px-6 py-28 border-t border-border">
        <div className="label-mono mb-3">— Process</div>
        <h2 className="text-4xl sm:text-5xl font-medium max-w-3xl leading-tight mb-16">
          De votre brief au site en ligne, <span className="text-muted-foreground italic font-light">en moins de 2 minutes.</span>
        </h2>
        <div className="grid md:grid-cols-4 gap-5">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="p-6 rounded-2xl border border-border bg-card"
            >
              <div className="text-5xl font-light text-primary/60">{s.n}</div>
              <div className="mt-6 font-medium">{s.title}</div>
              <div className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 py-28 border-t border-border">
        <div className="relative overflow-hidden rounded-3xl p-14 md:p-20 border border-border bg-card">
          <div className="absolute -bottom-32 -right-10 w-[500px] h-[500px] rounded-full bg-primary/30 blur-3xl pointer-events-none" />
          <div className="relative grid md:grid-cols-2 gap-8 items-center">
            <div>
              <div className="label-mono mb-3">— Prêt ?</div>
              <h2 className="text-4xl sm:text-5xl font-medium leading-tight">
                Lancez votre studio de sites IA maintenant.
              </h2>
              <p className="mt-4 text-muted-foreground text-lg">
                Gratuit pour le MVP. Stripe en préparation.
              </p>
            </div>
            <div className="flex md:justify-end gap-3">
              <Link to="/new" data-testid="final-cta" className="inline-flex items-center gap-2 px-7 py-4 rounded-full bg-primary text-primary-foreground font-medium btn-glow text-base">
                Commencer <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap gap-6 justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 rounded-md bg-primary" />
            AutoSite.AI Pro — © {new Date().getFullYear()}
          </div>
          <div className="flex gap-6">
            <Shield className="w-4 h-4" /> Validation backend
            <Globe className="w-4 h-4" /> SEO local
            <Zap className="w-4 h-4" /> &lt; 45s
          </div>
        </div>
      </footer>
    </div>
  );
}
