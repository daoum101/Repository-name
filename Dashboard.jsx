import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Plus, Copy, Trash2, ExternalLink, Clock, FolderOpen } from "lucide-react";
import Navbar from "@/components/Navbar";
import { listProjects, deleteProject, duplicateProject } from "@/lib/api";
import { SECTORS } from "@/data/sectors";

function secThumb(id) {
  const s = SECTORS.find((s) => s.id === id);
  return s?.thumb || SECTORS[0].thumb;
}

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setProjects(await listProjects());
    } catch (e) {
      toast.error("Impossible de charger les projets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const onDelete = async (id) => {
    if (!window.confirm("Supprimer ce projet ?")) return;
    await deleteProject(id);
    toast.success("Projet supprimé");
    load();
  };

  const onDuplicate = async (id) => {
    await duplicateProject(id);
    toast.success("Projet dupliqué");
    load();
  };

  return (
    <div className="dark min-h-screen">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-14">
        <div className="flex flex-wrap items-end justify-between gap-6 mb-12">
          <div>
            <div className="label-mono mb-3">— Studio</div>
            <h1 className="text-4xl sm:text-5xl font-medium tracking-tight">Mes projets</h1>
            <p className="text-muted-foreground mt-2">Gérez, dupliquez, éditez vos sites générés.</p>
          </div>
          <Link
            to="/new"
            data-testid="dashboard-new-btn"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-primary text-primary-foreground font-medium btn-glow"
          >
            <Plus className="w-4 h-4" /> Nouveau site
          </Link>
        </div>

        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="aspect-[4/3] rounded-2xl shimmer" />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="border border-dashed border-border rounded-3xl p-20 text-center" data-testid="dashboard-empty">
            <div className="w-14 h-14 rounded-2xl bg-card border border-border flex items-center justify-center mx-auto mb-5">
              <FolderOpen className="w-6 h-6 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-medium">Aucun projet pour l'instant</h3>
            <p className="text-muted-foreground mt-2">Créez votre premier site en moins d'une minute.</p>
            <Link to="/new" className="inline-flex items-center gap-2 mt-6 px-5 py-2.5 rounded-full bg-primary text-primary-foreground font-medium btn-glow">
              <Plus className="w-4 h-4" /> Créer un projet
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.04 }}
                className="group overflow-hidden rounded-2xl border border-border bg-card hover:border-primary/40 transition-colors"
                data-testid={`project-card-${p.id}`}
              >
                <Link to={`/projects/${p.id}`} className="block relative">
                  <div
                    className="aspect-[16/10] w-full bg-cover bg-center"
                    style={{ backgroundImage: `url(${secThumb(p.sector)})` }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent" />
                  <div className="absolute top-3 left-3 label-mono px-2 py-1 rounded-full bg-background/80 backdrop-blur-sm text-[10px]">
                    {p.sector}
                  </div>
                  {p.content ? (
                    <div className="absolute top-3 right-3 text-[10px] px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Généré
                    </div>
                  ) : (
                    <div className="absolute top-3 right-3 text-[10px] px-2 py-1 rounded-full bg-primary/20 text-primary border border-primary/30">
                      Brouillon
                    </div>
                  )}
                </Link>
                <div className="p-5 flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="font-medium truncate">{p.business_name}</h3>
                    <div className="text-xs text-muted-foreground mt-1 flex items-center gap-3">
                      <span>{p.city}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(p.updated_at).toLocaleDateString("fr-FR")}</span>
                    </div>
                  </div>
                  <div className="flex gap-1.5">
                    <Link to={`/projects/${p.id}`} title="Ouvrir" className="w-8 h-8 rounded-lg border border-border hover:border-primary/40 flex items-center justify-center" data-testid={`project-open-${p.id}`}>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                    <button onClick={() => onDuplicate(p.id)} title="Dupliquer" className="w-8 h-8 rounded-lg border border-border hover:border-primary/40 flex items-center justify-center" data-testid={`project-duplicate-${p.id}`}>
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => onDelete(p.id)} title="Supprimer" className="w-8 h-8 rounded-lg border border-border hover:border-destructive/60 hover:text-destructive flex items-center justify-center" data-testid={`project-delete-${p.id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
