import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "./api/client";
import { Layout, type Tab } from "./components/Layout";
import { EventsPage } from "./pages/EventsPage";
import { StatusPage } from "./pages/StatusPage";
import { WatchlistPage } from "./pages/WatchlistPage";

const TITLES: Record<Tab, string> = {
  events: "Événements récents",
  watchlist: "Plaques surveillées",
  status: "État des caméras",
};

export default function App() {
  const [tab, setTab] = useState<Tab>("events");
  const { data: cameras } = useQuery({ queryKey: ["cameras"], queryFn: api.cameras });
  const online = cameras?.filter((camera) => camera.state === "ACTIVE").length ?? 0;
  const total = cameras?.length ?? 0;

  return (
    <Layout
      tab={tab}
      onTab={setTab}
      header={
        <>
          <h1 className="text-lg font-semibold tracking-tight">{TITLES[tab]}</h1>
          <div className="flex items-center gap-3 text-sm text-muted">
            {api.usingMock && (
              <span className="rounded-full border border-line px-2.5 py-1 text-xs">
                démo · données fictives
              </span>
            )}
            <span>
              {online}/{total} caméras en ligne
            </span>
          </div>
        </>
      }
    >
      {tab === "events" && <EventsPage />}
      {tab === "watchlist" && <WatchlistPage />}
      {tab === "status" && <StatusPage />}
    </Layout>
  );
}
