# Sistema de Minería de Repositorios GitHub (Miner + Visualizer)

Proyecto de **Ingeniería de Datos** con arquitectura **productor-consumidor** usando dos contenedores:

- **miner** (Python): consulta GitHub, extrae nombres de funciones/métodos y tokeniza palabras.
- **visualizer** (Node.js + Express): consume lotes del miner, acumula ranking global y por lenguaje, y actualiza una UI en tiempo real con SSE.

---

## 1) Descripción del proyecto

El sistema analiza repositorios públicos de GitHub para obtener palabras frecuentes en identificadores de funciones y métodos de archivos:

- Python (`.py`) usando `ast`
- Java (`.java`) usando `tree-sitter`

El `miner` envía lotes al `visualizer` vía `POST /events`. El `visualizer` mantiene acumulados en memoria y muestra un ranking en un gráfico de barras (Chart.js) con actualización en tiempo real.

---

## 2) Arquitectura general

```text
GitHub API ---> miner (producer) ---> visualizer (consumer + SSE + UI)
```

- `miner`
  - Descubre repositorios por stars (descendente)
  - Recorre árboles git recursivos
  - Filtra `.py` / `.java`
  - Extrae funciones/métodos
  - Tokeniza identificadores
  - Publica lotes a `visualizer`
  - Persiste estado local en `/data`

- `visualizer`
  - Expone `POST /events`
  - Acumula conteos globales y por lenguaje
  - Expone API `GET /api/ranking`, `GET /api/stats`
  - Publica eventos SSE en `GET /stream`
  - Sirve frontend estático en `/`

---

## 3) Decisiones de diseño

1. **Acumulación global incremental**
   - Cada lote suma sobre el estado anterior (no reemplaza).
2. **Scopes de ranking**
   - `global`, `python`, `java`.
3. **Tiempo real con SSE**
   - Cada `POST /events` dispara broadcast a todos los clientes conectados.
4. **Simplicidad académica**
   - Sin frameworks frontend pesados (HTML/CSS/JS + Chart.js).
5. **Desacoplamiento por HTTP**
   - Productor y consumidor corren en contenedores independientes.

---

## 4) Stack utilizado

- **Miner**: Python 3.11+, `requests`, `ast`, `tree-sitter`
- **Visualizer backend**: Node.js 20, Express
- **Realtime**: Server-Sent Events (SSE)
- **Frontend**: HTML/CSS/JS + Chart.js
- **Orquestación**: Docker Compose

---

## 5) Cómo ejecutar (un solo comando)

1. Copiar variables de ejemplo:

```bash
cp .env.example .env
```

2. Completar `GITHUB_TOKEN` en `.env` (recomendado para evitar límites estrictos de la API).

3. Levantar todo:

```bash
docker compose up --build
```

4. Abrir visualización:

- UI: http://localhost:3000
- Health: http://localhost:3000/health

---

## 6) Variables de entorno

### Miner

- `GITHUB_TOKEN`: token GitHub (opcional pero recomendado)
- `VISUALIZER_URL`: endpoint del visualizer (default `http://visualizer:3000/events`)
- `STATE_DIR`: carpeta de estado (default `/data`)
- `MIN_STARS`: mínimo de estrellas para discovery
- `MAX_REPOS_PER_RUN`: repos máximos por iteración
- `BATCH_SLEEP_SECONDS`: pausa entre iteraciones
- `MAX_FILE_SIZE_BYTES`: límite de tamaño por archivo
- `LOG_LEVEL`: nivel de logs

### Visualizer

- `PORT`: puerto HTTP (default `3000`)
- `DEFAULT_TOP_N`: top por defecto para snapshots SSE

---

## 7) Flujo productor-consumidor

1. `miner` consulta GitHub Search API ordenado por stars.
2. `miner` obtiene árbol recursivo de cada repo y descarga blobs relevantes.
3. `miner` extrae nombres de funciones/métodos y tokeniza palabras.
4. `miner` envía un lote por repositorio a `visualizer` (`POST /events`).
5. `visualizer`:
   - acumula conteos en `global`, `python`, `java`
   - actualiza métricas acumuladas
   - emite actualización por SSE
6. Frontend recibe SSE y refresca métricas + gráfico automáticamente.

---

## 8) Ejemplo de payload (`POST /events`)

```json
{
  "repo": "pallets/flask",
  "stars": 69000,
  "files_processed": 12,
  "functions_found": 37,
  "language_counts": {
    "python": {
      "get": 10,
      "response": 4
    },
    "java": {
      "retain": 2
    }
  },
  "timestamp": "2026-03-20T12:00:00Z"
}
```

---

## 9) API del visualizer

- `POST /events` -> recibe lote del miner
- `GET /api/ranking?scope=global&top=10` -> ranking actual
  - `scope`: `global|python|java`
  - `top`: entero positivo
- `GET /api/stats` -> métricas acumuladas
- `GET /stream` -> stream SSE para updates en tiempo real
- `GET /` -> frontend estático

---

## 10) Supuestos y limitaciones

- El ranking del visualizer es **en memoria**: al reiniciar el contenedor se resetea.
- El estado persistente está del lado del miner (`./data:/data`) para evitar reprocesar repos.
- La API de GitHub tiene rate limits; usar `GITHUB_TOKEN` mejora estabilidad.
- El particionado por estrellas del miner es una estrategia razonable y extensible para el contexto de la tarea.

---

## Estructura del repositorio

```text
.
├── miner/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── visualizer/
│   ├── src/
│   │   ├── routes/
│   │   ├── rankingStore.js
│   │   └── server.js
│   ├── public/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```
