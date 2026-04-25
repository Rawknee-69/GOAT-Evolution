import { motion } from "framer-motion";

export function AgentCard({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <motion.div layout initial={{ opacity: 0.6 }} animate={{ opacity: 1 }} className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-slate-400">{subtitle}</p>
    </motion.div>
  );
}
