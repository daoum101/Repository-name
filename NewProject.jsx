import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import Navbar from "@/components/Navbar";
import { createProject, generateProject } from "@/lib/api";
import { SECTORS, STYLES, TONES, OBJECTIVES, DESIGN_LEVELS } from "@/data/sectors";

const STEPS = [
  { key: "sector", label: "Secteur" },
  { key: "identity", label: "Identité" },
  { key: "contact", label: "Contact & Ville" },
  { key: "style", label: "Style" },
  { key: "content", label: "Contenu" },
  { key: "review", label: "Génération" },
];

export default function NewProject() {
  const nav = useNavigate();
  const location = useLocation();
  const [step, setStep] = useState(0);
  const [generating, setGenerating] = useState(false);

  const [form, setForm] = useState({
    sector: location.state?.sector || "",
    business_name: "",
    description: "",
    city: "",
    address: "",
    phone: "",
    email: "",
    whatsapp: "",
    objective: OBJECTIVES[0],
    style: "moderne",
    primary_color: "#FF4500",
    secondary_color: "#0A0A0A",
    tone: "Professionnel",
    services: "",
    audience: "",
    main_button: "Contactez-nous",
    design_level: "premium",
  });

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const canNext = () => {
    if (step === 0) return !!form.sector;
    if (step === 1) return form.business_name.length > 1;
    if (step === 2) return form.city.length > 1;
    return true;
  };

  const onGenerate = async () => {
    setGenerating(true);
    try {
      const project = await createProject(form);
      toast.success("Projet créé. L'IA écrit votre site…");
      const generated = await generateProject(project.id);
      toast.success("Site généré ✦");
      nav(`/projects/${generated.id}`);
    } catch (e) {
      console.error(e);
      toast.error(e?.response?.data?.detail || "Erreur lors de la génération");
      setGenerating(false);
    }
  };

  return (
    <div className="dark min-h-screen">
      <Navbar />
      <main className="max-w-5xl mx-auto px-6 py-14">
        <div className="mb-10">
          <div className="label-mono mb-3">— Nouveau projet</div>
          <h1 className="text-4xl sm:text-5xl font-medium tracking-tight">Brief intelligent</h1>
          <p className="text-muted-foreground mt-2">Plus votre brief est précis, plus le site sera pertinent.</p>
        </div>

        {/* Stepper */}
        <div className="flex items-center gap-3 mb-10 overflow-x-auto pb-2">
          {STEPS.map((s, i) => (
            <div key={s.key} className="flex items-center gap-3 flex-shrink-0">
              <div
                className={`w-8 h-8 rounded-full border flex items-center justify-center text-xs font-medium transition-all ${
                  i < step
                    ? "bg-primary text-primary-foreground border-primary"
                    : i === step
                    ? "border-primary text-primary"
                    : "border-border text-muted-foreground"
                }`}
              >
                {i < step ? <Check className="w-3.5 h-3.5" /> : i + 1}
              </div>
              <span className={`text-sm ${i === step ? "text-foreground" : "text-muted-foreground"}`}>{s.label}</span>
              {i < STEPS.length - 1 && <div className="w-6 h-px bg-border" />}
            </div>
          ))}
        </div>

        {/* Steps */}
        {generating ? (
          <GenerationLoader />
        ) : (
          <div className="rounded-3xl border border-border bg-card p-8 md:p-12">
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -30 }}
                transition={{ duration: 0.3 }}
              >
                {step === 0 && <SectorStep form={form} set={set} />}
                {step === 1 && <IdentityStep form={form} set={set} />}
                {step === 2 && <ContactStep form={form} set={set} />}
                {step === 3 && <StyleStep form={form} set={set} />}
                {step === 4 && <ContentStep form={form} set={set} />}
                {step === 5 && <ReviewStep form={form} />}
              </motion.div>
            </AnimatePresence>

            <div className="flex items-center justify-between mt-10 pt-6 border-t border-border">
              <button
                onClick={() => setStep((s) => Math.max(0, s - 1))}
                disabled={step === 0}
                data-testid="wizard-prev"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm text-muted-foreground hover:text-foreground disabled:opacity-40"
              >
                <ArrowLeft className="w-4 h-4" /> Retour
              </button>
              {step < STEPS.length - 1 ? (
                <button
                  onClick={() => canNext() && setStep((s) => s + 1)}
                  disabled={!canNext()}
                  data-testid="wizard-next"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground text-sm font-medium btn-glow disabled:opacity-50"
                >
                  Continuer <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={onGenerate}
                  data-testid="wizard-generate"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-primary text-primary-foreground font-medium btn-glow"
                >
                  Générer avec l'IA <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function Field({ label, children, hint }) {
  return (
    <label className="block">
      <div className="label-mono mb-2">{label}</div>
      {children}
      {hint && <div className="text-xs text-muted-foreground mt-1.5">{hint}</div>}
    </label>
  );
}
const inputCls =
  "w-full bg-input/50 border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/60 transition-colors placeholder:text-muted-foreground";

function SectorStep({ form, set }) {
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Choisissez votre secteur</h2>
      <p className="text-muted-foreground mb-8 text-sm">L'IA adapte le ton, les sections et la structure selon votre métier.</p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {SECTORS.map((s) => {
          const selected = form.sector === s.id;
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => set("sector", s.id)}
              data-testid={`sector-${s.id}`}
              className={`relative overflow-hidden rounded-2xl border text-left transition-all ${
                selected ? "border-primary ring-2 ring-primary/30" : "border-border hover:border-primary/40"
              }`}
            >
              <div className="aspect-[16/10] bg-cover bg-center" style={{ backgroundImage: `url(${s.thumb})` }} />
              <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/30 to-transparent" />
              <div className="absolute bottom-0 inset-x-0 p-4 flex items-center justify-between">
                <span className="font-medium">{s.name}</span>
                {selected && <Check className="w-4 h-4 text-primary" />}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function IdentityStep({ form, set }) {
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Votre identité</h2>
      <p className="text-muted-foreground mb-8 text-sm">Le nom et la description guident toute la rédaction du site.</p>
      <div className="grid md:grid-cols-2 gap-5">
        <Field label="Nom de l'entreprise">
          <input data-testid="input-business-name" className={inputCls} value={form.business_name} onChange={(e) => set("business_name", e.target.value)} placeholder="Ex: Pizza Napoli" />
        </Field>
        <Field label="Public cible">
          <input data-testid="input-audience" className={inputCls} value={form.audience} onChange={(e) => set("audience", e.target.value)} placeholder="Ex: Familles, étudiants, locaux…" />
        </Field>
        <div className="md:col-span-2">
          <Field label="Description de l'activité">
            <textarea data-testid="input-description" rows={4} className={inputCls} value={form.description} onChange={(e) => set("description", e.target.value)} placeholder="En quelques phrases, expliquez ce que vous faites et ce qui vous distingue." />
          </Field>
        </div>
        <Field label="Objectif principal">
          <select data-testid="input-objective" className={inputCls} value={form.objective} onChange={(e) => set("objective", e.target.value)}>
            {OBJECTIVES.map((o) => <option key={o}>{o}</option>)}
          </select>
        </Field>
        <Field label="Bouton principal (CTA)">
          <input data-testid="input-main-button" className={inputCls} value={form.main_button} onChange={(e) => set("main_button", e.target.value)} placeholder="Ex: Réserver" />
        </Field>
      </div>
    </div>
  );
}

function ContactStep({ form, set }) {
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Localisation & contact</h2>
      <p className="text-muted-foreground mb-8 text-sm">Essentiel pour le SEO local et le schema.org LocalBusiness.</p>
      <div className="grid md:grid-cols-2 gap-5">
        <Field label="Ville *"><input data-testid="input-city" className={inputCls} value={form.city} onChange={(e) => set("city", e.target.value)} placeholder="Ex: Bruxelles" /></Field>
        <Field label="Adresse"><input data-testid="input-address" className={inputCls} value={form.address} onChange={(e) => set("address", e.target.value)} placeholder="Ex: 12 Rue de la Paix" /></Field>
        <Field label="Téléphone"><input data-testid="input-phone" className={inputCls} value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+32 ..." /></Field>
        <Field label="WhatsApp"><input data-testid="input-whatsapp" className={inputCls} value={form.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} placeholder="+32 ..." /></Field>
        <Field label="Email"><input data-testid="input-email" className={inputCls} value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="contact@..." /></Field>
      </div>
    </div>
  );
}

function StyleStep({ form, set }) {
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Style visuel</h2>
      <p className="text-muted-foreground mb-8 text-sm">Ton et couleurs définissent l'ambiance générale du site.</p>
      <div className="grid md:grid-cols-2 gap-5">
        <div className="md:col-span-2">
          <div className="label-mono mb-3">Ambiance</div>
          <div className="grid sm:grid-cols-3 gap-3">
            {STYLES.map((s) => (
              <button key={s.id} type="button" data-testid={`style-${s.id}`} onClick={() => set("style", s.id)}
                className={`p-5 rounded-2xl border text-left transition ${form.style === s.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"}`}>
                <div className="font-medium">{s.name}</div>
                <div className="text-xs text-muted-foreground mt-1">{s.description}</div>
              </button>
            ))}
          </div>
        </div>
        <Field label="Ton">
          <select data-testid="input-tone" className={inputCls} value={form.tone} onChange={(e) => set("tone", e.target.value)}>
            {TONES.map((t) => <option key={t}>{t}</option>)}
          </select>
        </Field>
        <Field label="Niveau design">
          <select data-testid="input-design-level" className={inputCls} value={form.design_level} onChange={(e) => set("design_level", e.target.value)}>
            {DESIGN_LEVELS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </Field>
        <Field label="Couleur principale">
          <div className="flex items-center gap-3">
            <input type="color" data-testid="input-primary-color" value={form.primary_color} onChange={(e) => set("primary_color", e.target.value)} className="w-12 h-12 rounded-lg bg-transparent cursor-pointer border border-border" />
            <input className={inputCls + " flex-1 font-mono text-xs"} value={form.primary_color} onChange={(e) => set("primary_color", e.target.value)} />
          </div>
        </Field>
        <Field label="Couleur de fond (secondaire)">
          <div className="flex items-center gap-3">
            <input type="color" data-testid="input-secondary-color" value={form.secondary_color} onChange={(e) => set("secondary_color", e.target.value)} className="w-12 h-12 rounded-lg bg-transparent cursor-pointer border border-border" />
            <input className={inputCls + " flex-1 font-mono text-xs"} value={form.secondary_color} onChange={(e) => set("secondary_color", e.target.value)} />
          </div>
        </Field>
      </div>
    </div>
  );
}

function ContentStep({ form, set }) {
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Contenu</h2>
      <p className="text-muted-foreground mb-8 text-sm">L'IA rédigera tout — mais ces indications orientent la génération.</p>
      <Field label="Services / produits (liste libre)">
        <textarea data-testid="input-services" rows={5} className={inputCls} value={form.services} onChange={(e) => set("services", e.target.value)} placeholder="Ex: Coupe homme, barbe sculptée, coloration, rasage traditionnel…" />
      </Field>
    </div>
  );
}

function ReviewStep({ form }) {
  const sector = SECTORS.find((s) => s.id === form.sector);
  return (
    <div>
      <h2 className="text-2xl font-medium mb-2">Tout est prêt</h2>
      <p className="text-muted-foreground mb-8 text-sm">Dernière vérification avant la génération par Claude Sonnet 4.5.</p>
      <div className="grid md:grid-cols-2 gap-4 text-sm">
        {[
          ["Entreprise", form.business_name],
          ["Secteur", sector?.name],
          ["Ville", form.city],
          ["Objectif", form.objective],
          ["Ton", form.tone],
          ["Style", form.style],
          ["Niveau design", form.design_level],
          ["Couleur principale", form.primary_color],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between p-4 rounded-xl border border-border bg-background/50">
            <span className="text-muted-foreground">{k}</span>
            <span className="font-medium truncate max-w-[60%] text-right">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function GenerationLoader() {
  return (
    <div className="rounded-3xl border border-border bg-card p-12 text-center">
      <div className="inline-flex items-center gap-2 label-mono mb-6">
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        Claude Sonnet 4.5 travaille
      </div>
      <h2 className="text-3xl sm:text-4xl font-medium tracking-tight max-w-xl mx-auto">
        Génération de votre site premium en cours.
      </h2>
      <p className="text-muted-foreground mt-3">Structure, copy marketing, FAQ, SEO local, schema.org — tout est rédigé.</p>
      <div className="mt-10 space-y-3 max-w-xl mx-auto">
        {["Analyse du brief", "Architecture du site", "Rédaction marketing", "SEO & schema.org", "Assemblage final"].map((l, i) => (
          <div key={l} className="flex items-center gap-3 text-sm">
            <span className="label-mono text-primary">0{i + 1}</span>
            <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
              <div className="h-full tracing-beam bg-primary/30" />
            </div>
            <span className="text-muted-foreground">{l}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
