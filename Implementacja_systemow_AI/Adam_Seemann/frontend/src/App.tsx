import { Route, Routes } from "react-router-dom";

import { MainLayout } from "./layout/MainLayout";
import { Home } from "./pages/Home";
import { Stock } from "./pages/Stock";

export default function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/stock/:ticker" element={<Stock />} />
      </Routes>
    </MainLayout>
  );
}