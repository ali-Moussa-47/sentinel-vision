import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { EventCard } from "../components/EventCard";

export function EventsPage() {
  const { data, isLoading } = useQuery({ queryKey: ["events"], queryFn: api.events });
  if (isLoading) return <p className="text-muted">Chargement…</p>;
  if (!data || data.length === 0) return <p className="text-muted">Aucun événement.</p>;
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
      {data.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}
