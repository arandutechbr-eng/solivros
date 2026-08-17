import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { BookDetailPage } from "./pages/BookDetailPage";
import { BookNewPage } from "./pages/BookNewPage";
import { BookReadPage } from "./pages/BookReadPage";
import { BookReviewPage } from "./pages/BookReviewPage";
import { BooksPage } from "./pages/BooksPage";
import { DashboardPage } from "./pages/DashboardPage";
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/books" element={<BooksPage />} />
          <Route path="/books/new" element={<BookNewPage />} />
          <Route path="/books/:id" element={<BookDetailPage />} />
          <Route path="/books/:id/review" element={<BookReviewPage />} />
          <Route path="/books/:id/read" element={<BookReadPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
