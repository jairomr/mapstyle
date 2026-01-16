/**
 * Types baseados na API FastAPI
 * Compatível com scr/api/schemas/symbology_schema.py
 */

export type SymbologyGeometryType = 'POLYGON' | 'LINE' | 'POINT';

export type SymbologyFill =
  | 'SOLID'
  | 'NOBRUSH'
  | 'SLASH'
  | 'BACKSLASH'
  | 'PIPE'
  | 'DASH'
  | 'PLUS'
  | 'X'
  | 'O_LOWER'
  | 'O_UPPER'
  | 'DOT'
  | 'STAR';

export type MarkerType =
  | 'CIRCLE'
  | 'SQUARE'
  | 'TRIANGLE'
  | 'STAR'
  | 'CROSS'
  | 'DIAMOND'
  | 'PENTAGON'
  | 'HEXAGON'
  | 'ARROW'
  | 'VERTICAL_ARROW'
  | 'X_MARK'
  | 'PLUS_MARK';

// Union type para fill_style que pode ser tanto SymbologyFill quanto MarkerType
export type FillStyleOrMarker = SymbologyFill | MarkerType;

export type LineStyle =
  | 'SOLID'
  | 'DASHED'
  | 'DOTTED'
  | 'DASH_DOT'
  | 'LONG_DASH'
  | 'SHORT_DASH'
  | 'DASH_DOT_DOT'
  | 'DASH_DOT_DOT_DOT'
  | 'SPARSE_DOT'
  | 'DENSE_DOT'
  | 'NONE';

/**
 * Payload para criar simbologia
 * POST /api/symbology
 *
 * Nota: symbology_fill_style é SymbologyFill para POLYGON/LINE
 *       e MarkerType para POINT
 */
export interface SymbologyCreate {
  symbology_geometry_type: SymbologyGeometryType;
  symbology_fill_color: string;
  symbology_fill_style: FillStyleOrMarker;
  symbology_fill_density: number;
  symbology_stroke_color: string;
  symbology_stroke_style: LineStyle;
  symbology_stroke_line: number;
}

/**
 * Simbologia serializada (response)
 */
export interface SymbologyData extends SymbologyCreate {}

/**
 * Response de POST /api/symbology
 */
export interface SymbologyResponse {
  url_key: string;
  matplotlib_url: string;
  preview_url: string;
  symbology: SymbologyData;
}

/**
 * Configurações do matplotlib
 */
export interface MatplotlibConfig {
  fill: boolean;
  facecolor?: string;
  edgecolor?: string;
  linewidth: number;
  linestyle?: string;
  hatch?: string;
  radius?: number;
}

/**
 * Configurações do GeoServer
 */
export interface GeoServerConfig {
  sld: string;
  css: string;
  rest_payload: Record<string, unknown>;
}

/**
 * Response de GET /api/result/{url_key}/json
 */
export interface ConfigResponse {
  url_key: string;
  matplotlib: MatplotlibConfig;
  geoserver: GeoServerConfig;
  symbology: SymbologyData;
}

/**
 * Estado do formulário
 */
export interface FormState extends SymbologyCreate {}

/**
 * Estado da aplicação
 */
export interface AppState {
  formState: FormState;
  urlKey: string | null;
  config: ConfigResponse | null;
  isLoading: boolean;
  error: string | null;
}
