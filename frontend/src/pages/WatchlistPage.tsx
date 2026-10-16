import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { type FormEvent, useState } from "react";
import { api } from "../api/client";
import type { WatchedPlate } from "../api/types";

export function WatchlistPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["plates"], queryFn: api.watchlist });
  const [value, setValue] = useState("");

  const write = (plates: WatchedPlate[]) => queryClient.setQueryData(["plates"], plates);

  const add = useMutation({
    mutationFn: () => api.addPlate(value),
    onSuccess: (plates) => {
      write(plates);
      setValue("");
    },
  });
  const remove = useMutation({
    mutationFn: (plate: string) => api.removePlate(plate),
    onSuccess: write,
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (value.trim()) add.mutate();
  };

  return (
    <div className="max-w-xl space-y-6">
      <form onSubmit={submit} className="flex gap-3">
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Nouvelle plaque, ex. AB123CD"
          className="flex-1 rounded-xl border border-line bg-panel px-4 py-2.5 text-sm tracking-wider outline-none focus:border-brand"
        />
        <button
          type="submit"
          className="rounded-xl bg-brand px-4 py-2.5 text-sm font-medium text-bg"
        >
          Ajouter
        </button>
      </form>
      <ul className="divide-y divide-line overflow-hidden rounded-2xl border border-line bg-panel">
        {data?.map((plate) => (
          <li key={plate.value} className="flex items-center justify-between px-4 py-3">
            <span className="font-mono tracking-wider">{plate.value}</span>
            <button
              type="button"
              onClick={() => remove.mutate(plate.value)}
              className="text-muted transition hover:text-alert"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
