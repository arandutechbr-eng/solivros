import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Painel" },
  { to: "/conteudo", label: "Conteúdo" },
  { to: "/simulados", label: "Simulados" },
  { to: "/desempenho", label: "Desempenho" },
];

export function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <NavLink to="/" className="text-lg font-semibold tracking-tight text-amber-300">
            Solivros Simulados
          </NavLink>
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
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
