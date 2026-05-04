import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { toast } from "sonner";
import {
  Monitor, Tablet, Smartphone, Download, RefreshCw,
  Gauge, Palette, Save, ArrowLeft,
} from "lucide-react";
import { getProject, generateProject, getSeoScore, updateProject, previewUrl, exportUrl, API } from "@/lib/api";
import SEOScore from "@/components/SEOScore";
import ThemeToggle from "@/components/ThemeToggle";

const DEVICES = {
  desktop: { icon: Monitor, w: "100%", label: "Desktop" },
  tablet: { icon: Tablet, w: "820px", label: "Tablette" },
  mobile: { icon: Smartphone, w: "400px", label: "Mobile" },
};

export default function Editor() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [device, setDevice] = useState("desktop");
  const [generating, setGenerating] = useState(false);
  const [tab, setTab] = useState("design");
  const [seo, setSeo] = useState(null);
  const [previewKey, setPreviewKey] = useState(0);

  const load = async () => {
    const p = await getProject(id);
    setProject(p);
    if (p.content) {
      try { setSeo(await getSeoScore(id)); } catch {}
    }
  };

  useEffect(() => { load(); }, [id]);

  const onRegenerate = async () => {
    setGenerating(true);
    try {
      const updated = await generateProject(id);
      setProject(updated);
      setSeo(await getSeoScore(id));
      setPreviewKey((k) => k + 1);
      toast.success("Site regénéré");
    } catch (e) {
      toast.error("Erreur de génération");
    } finally {
      setGenerating(false);
    }
  };

  const onColorChange = async (field, value) => {
    setProject((p) => ({ ...p, [field]: value }));
  };

  const onSave = async () => {
    await updateProject(id, {
      primary_color: project.primary_color,
      secondary_color: project.secondary_color,
      business_name: project.business_name,
    });
    setPreviewKey((k) => k + 1);
    toast.success("Modifications enregistrées");
  };

  if (!project) {
    return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Chargement…</div>;
  }

  const hasContent = !!project.content;

  return (
    <div className="dark min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="sticky top-0 z-30 backdrop-blur-xl bg-background/80 border-b border-border">
        <div className="px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <Link to="/dashboard" className="text-muted-foreground hover:text-foreground" data-testid="editor-back">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="min-w-0">
              <div className="text-sm font-medium truncate">{project.business_name}</div>
              <div className="label-mono !text-[9px] truncate">{project.sector} · {project.city}</div>
            </div>
          </div>

          <div className="flex items-center gap-1 bg-card border border-border rounded-full p-1">
            {Object.entries(DEVICES).map(([k, d]) => (
              <button
                key={k}
                onClick={() => setDevice(k)}
                data-testid={`device-${k}`}
                title={d.label}
                className={`w-9 h-8 rounded-full flex items-center justify-center transition-colors ${
                  device === k ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <d.icon className="w-4 h-4" />
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button
              onClick={onRegenerate}
              disabled={generating}
              data-testid="editor-regenerate"
              className="inline-flex items-center gap-2 px-3 py-2 rounded-full text-sm border border-border hover:border-primary/40 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${generating ? "animate-spin" : ""}`} />
              {hasContent ? "Regénérer" : "Générer"}
            </button>
            <a
              href={hasContent ? exportUrl(id) : "#"}
              data-testid="editor-export"
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
                hasContent ? "bg-primary text-primary-foreground btn-glow" : "bg-muted text-muted-foreground pointer-events-none"
              }`}
            >
              <Download className="w-3.5 h-3.5" /> Export ZIP
            </a>
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 flex min-h-0">
        {/* Sidebar */}
        <aside className="w-80 border-r border-border bg-card/30 flex flex-col">
          <div className="flex border-b border-border">
            {[
              { k: "design", icon: Palette, label: "Design" },
              { k: "seo", icon: Gauge, label: "SEO" },
            ].map((t) => (
              <button
                key={t.k}
                onClick={() => setTab(t.k)}
                data-testid={`tab-${t.k}`}
                className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                  tab === t.k ? "text-foreground border-b-2 border-primary" : "text-muted-foreground"
                }`}
              >
                <t.icon className="w-4 h-4" /> {t.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-5">
            {tab === "design" && (
              <>
                <div>
                  <div className="label-mono mb-2">Nom</div>
                  <input
                    data-testid="edit-name"
                    className="w-full bg-input/50 border border-border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-primary/60"
                    value={project.business_name}
                    onChange={(e) => setProject({ ...project, business_name: e.target.value })}
                  />
                </div>

                <div>
                  <div className="label-mono mb-2">Couleur principale</div>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      data-testid="edit-primary"
                      value={project.primary_color}
                      onChange={(e) => onColorChange("primary_color", e.target.value)}
                      className="w-10 h-10 rounded-lg cursor-pointer bg-transparent border border-border"
                    />
                    <input
                      className="flex-1 bg-input/50 border border-border rounded-xl px-3 py-2 text-xs font-mono focus:outline-none focus:border-primary/60"
                      value={project.primary_color}
                      onChange={(e) => onColorChange("primary_color", e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <div className="label-mono mb-2">Couleur de fond</div>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      data-testid="edit-secondary"
                      value={project.secondary_color}
                      onChange={(e) => onColorChange("secondary_color", e.target.value)}
                      className="w-10 h-10 rounded-lg cursor-pointer bg-transparent border border-border"
                    />
                    <input
                      className="flex-1 bg-input/50 border border-border rounded-xl px-3 py-2 text-xs font-mono focus:outline-none focus:border-primary/60"
                      value={project.secondary_color}
                      onChange={(e) => onColorChange("secondary_color", e.target.value)}
                    />
                  </div>
                </div>

                <button
                  onClick={onSave}
                  data-testid="edit-save"
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-full bg-primary text-primary-foreground text-sm font-medium btn-glow"
                >
                  <Save className="w-3.5 h-3.5" /> Enregistrer & rafraîchir
                </button>

                <div className="pt-4 border-t border-border">
                  <div className="label-mono mb-2">Versions</div>
                  <div className="text-xs text-muted-foreground">
                    {(project.versions?.length || 0)} sauvegarde(s) automatique(s)
                  </div>
                </div>

                {hasContent && (
                  <div className="pt-4 border-t border-border">
                    <div className="label-mono mb-2">Sections générées</div>
                    <ul className="text-xs space-y-1 text-muted-foreground">
                      {Object.keys(project.content).map((k) => (
                        <li key={k} className="flex items-center gap-2">
                          <span className="w-1 h-1 rounded-full bg-primary" /> {k}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {tab === "seo" && (
              hasContent ? (
                seo ? <SEOScore data={seo} /> : <div className="text-sm text-muted-foreground">Chargement…</div>
              ) : (
                <div className="text-sm text-muted-foreground">Générez d'abord le site pour obtenir un score SEO.</div>
              )
            )}
          </div>
        </aside>

        {/* Preview */}
        <main className="flex-1 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.08),transparent_50%)] p-6 overflow-auto">
          {generating ? (
            <div className="h-full rounded-2xl border border-border bg-card flex flex-col items-center justify-center p-10">
              <div className="inline-flex items-center gap-2 label-mono mb-4">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                Régénération en cours
              </div>
              <h3 className="text-2xl font-medium">Claude Sonnet 4.5 réécrit votre site…</h3>
              <div className="w-80 h-2 rounded-full bg-muted overflow-hidden mt-8">
                <div className="h-full tracing-beam bg-primary/30" />
              </div>
            </div>
          ) : (
            <div className="mx-auto transition-all duration-500 h-full" style={{ width: DEVICES[device].w, maxWidth: "100%" }}>
              <div className="rounded-2xl overflow-hidden border border-border shadow-2xl bg-black h-full min-h-[600px]">
                <iframe
                  key={previewKey}
                  data-testid="preview-iframe"
                  title="preview"
                  src={`${previewUrl(id)}?v=${previewKey}`}
                  className="w-full h-full min-h-[600px] bg-black"
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
