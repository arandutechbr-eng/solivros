import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { ChapterPage } from "./pages/ChapterPage";
import { ContentPage } from "./pages/ContentPage";
import { CustomQuizPage } from "./pages/CustomQuizPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ProgressPage } from "./pages/ProgressPage";
import { QuizzesPage } from "./pages/QuizzesPage";
import { ResultPage } from "./pages/ResultPage";
import { TakeQuizPage } from "./pages/TakeQuizPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/conteudo" element={<ContentPage />} />
          <Route path="/conteudo/:chapterId" element={<ChapterPage />} />
          <Route path="/simulados" element={<QuizzesPage />} />
          <Route path="/simulados/personalizado" element={<CustomQuizPage />} />
          <Route path="/simulados/:attemptId" element={<TakeQuizPage />} />
          <Route path="/resultados/:attemptId" element={<ResultPage />} />
          <Route path="/desempenho" element={<ProgressPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
