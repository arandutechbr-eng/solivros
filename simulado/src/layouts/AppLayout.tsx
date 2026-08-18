import { NavLink, Outlet } from "react-router-dom";
import { useSubject } from "../context/SubjectContext";

const links = [
  { to: "/", label: "Painel" },
  { to: "/conteudo", label: "Conteúdo" },
  { to: "/simulados", label: "Simulados" },
  { to: "/desempenho", label: "Desempenho" },
];

export function AppLayout() {
  const { subjects, subjectId, setSubjectId } = useSubject();

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <NavLink to="/" className="text-lg font-semibold tracking-tight text-amber-300">
            Solivros Simulados
          </NavLink>
          <div className="flex items-center gap-4">
            {subjects.length > 0 && (
              <label className="flex items-center gap-2 text-sm text-slate-400">
                <span className="hidden sm:inline">Matéria</span>
                <select
                  value={subjectId}
                  onChange={(event) => setSubjectId(event.target.value)}
                  className="max-w-40 rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100 sm:max-w-none"
                >
                  {subjects.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.title}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <nav className="flex gap-6 text-sm">
              {links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === "/"}
                  className={({ isActive }) =>
                    isActive ? "font-medium text-amber-300" : "text-slate-400 hover:text-slate-100"
                  }
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
