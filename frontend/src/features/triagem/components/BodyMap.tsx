interface BodyMapProps {
  regioesSelecionadas: string[];
  onToggleRegiao: (regiao: string) => void;
}

interface RegiaoBodyMap {
  nome: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rx?: number;
}

const REGIOES: RegiaoBodyMap[] = [
  { nome: "cabeca", x: 130, y: 15, width: 40, height: 40, rx: 20 },
  { nome: "pescoco", x: 143, y: 55, width: 14, height: 18, rx: 7 },
  { nome: "torax_esquerdo", x: 95, y: 78, width: 45, height: 55, rx: 18 },
  { nome: "torax_direito", x: 160, y: 78, width: 45, height: 55, rx: 18 },
  { nome: "abdome_superior", x: 110, y: 137, width: 80, height: 42, rx: 16 },
  { nome: "abdome_inferior", x: 112, y: 182, width: 76, height: 38, rx: 16 },
  { nome: "braco_esquerdo", x: 58, y: 84, width: 28, height: 108, rx: 14 },
  { nome: "braco_direito", x: 214, y: 84, width: 28, height: 108, rx: 14 },
  { nome: "perna_esquerda", x: 118, y: 224, width: 28, height: 120, rx: 14 },
  { nome: "perna_direita", x: 154, y: 224, width: 28, height: 120, rx: 14 },
];

function formatarNomeRegiao(regiao: string): string {
  return regiao.replaceAll("_", " ");
}

export function BodyMap({
  regioesSelecionadas,
  onToggleRegiao,
}: BodyMapProps) {
  return (
    <section className="space-y-5">
      <div>
        <h2 className="font-serif text-2xl text-slate-900">Localizacao da queixa</h2>
        <p className="text-sm text-slate-500">
          Marque a regiao predominante para complementar a descricao clinica.
        </p>
      </div>

      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <svg
          viewBox="0 0 300 360"
          role="img"
          aria-label="Mapa corporal - selecione a regiao da queixa"
          className="mx-auto h-[26rem] w-full max-w-sm"
        >
          <path
            d="M150 12
               C132 12 120 26 120 44
               C120 58 130 68 138 74
               L138 82
               C112 88 98 104 96 132
               L96 208
               L112 220
               L118 344
               L146 344
               L150 232
               L154 344
               L182 344
               L188 220
               L204 208
               L204 132
               C202 104 188 88 162 82
               L162 74
               C170 68 180 58 180 44
               C180 26 168 12 150 12Z"
            fill="#F8FAFC"
            stroke="#CBD5E1"
            strokeWidth="4"
          />

          {REGIOES.map((regiao) => {
            const selecionada = regioesSelecionadas.includes(regiao.nome);

            return (
              <rect
                key={regiao.nome}
                x={regiao.x}
                y={regiao.y}
                width={regiao.width}
                height={regiao.height}
                rx={regiao.rx ?? 12}
                role="button"
                tabIndex={0}
                aria-pressed={selecionada}
                aria-label={formatarNomeRegiao(regiao.nome)}
                onClick={() => onToggleRegiao(regiao.nome)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onToggleRegiao(regiao.nome);
                  }
                }}
                fill={selecionada ? "rgba(37, 99, 235, 0.4)" : "rgba(37, 99, 235, 0.08)"}
                stroke={selecionada ? "#2563EB" : "#94A3B8"}
                strokeWidth={selecionada ? 3 : 1.5}
                className="cursor-pointer transition hover:fill-[rgba(37,99,235,0.2)]"
              />
            );
          })}
        </svg>

        <div className="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          {regioesSelecionadas.length === 0 ? (
            <span>Nenhuma regiao selecionada.</span>
          ) : (
            <span>
              Regioes selecionadas:{" "}
              <strong>{regioesSelecionadas.map(formatarNomeRegiao).join(", ")}</strong>
            </span>
          )}
        </div>
      </div>
    </section>
  );
}
