import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { getSubjects } from "../services/simulado";
import type { SubjectPublic } from "../types";

const STORAGE_KEY = "solivros-subject-id";

type SubjectContextValue = {
  subjects: SubjectPublic[];
  subjectId: string;
  subject: SubjectPublic | null;
  setSubjectId: (id: string) => void;
  loading: boolean;
};

const SubjectContext = createContext<SubjectContextValue | null>(null);

function readStoredSubjectId(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || "portugues";
  } catch {
    return "portugues";
  }
}

export function SubjectProvider({ children }: { children: ReactNode }) {
  const [subjects, setSubjects] = useState<SubjectPublic[]>([]);
  const [subjectId, setSubjectIdState] = useState(readStoredSubjectId);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSubjects()
      .then((items) => {
        setSubjects(items);
        setSubjectIdState((current) => {
          if (items.length && !items.some((item) => item.id === current)) {
            const next = items[0].id;
            try {
              localStorage.setItem(STORAGE_KEY, next);
            } catch {
              /* ignore quota / private mode */
            }
            return next;
          }
          return current;
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const setSubjectId = useCallback((id: string) => {
    setSubjectIdState(id);
    try {
      localStorage.setItem(STORAGE_KEY, id);
    } catch {
      /* ignore quota / private mode */
    }
  }, []);

  const value = useMemo<SubjectContextValue>(
    () => ({
      subjects,
      subjectId,
      subject: subjects.find((item) => item.id === subjectId) ?? null,
      setSubjectId,
      loading,
    }),
    [subjects, subjectId, loading, setSubjectId],
  );

  return <SubjectContext.Provider value={value}>{children}</SubjectContext.Provider>;
}

export function useSubject() {
  const context = useContext(SubjectContext);
  if (!context) {
    throw new Error("useSubject precisa estar dentro de SubjectProvider");
  }
  return context;
}
