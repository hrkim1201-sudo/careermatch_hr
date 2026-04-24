import { Route, Routes } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import ProgramsPage from "./pages/ProgramsPage.jsx";
import MatchResultPage from "./pages/MatchResultPage.jsx";
import QualificationsPage from "./pages/QualificationsPage.jsx";
import JobsPage from "./pages/JobsPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/programs" element={<ProgramsPage />} />
      <Route path="/match" element={<MatchResultPage />} />
      <Route path="/qualifications" element={<QualificationsPage />} />
      <Route path="/jobs" element={<JobsPage />} />
    </Routes>
  );
}
