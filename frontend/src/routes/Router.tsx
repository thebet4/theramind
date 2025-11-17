import { Route, Routes } from "react-router";

import Home from "../pages/landing/index";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  );
}
