import axios, { AxiosInstance } from 'axios';
import {
  SymbologyCreate,
  SymbologyResponse,
  ConfigResponse,
} from '../types/symbology';

class SymbologyAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Criar uma nova simbologia
   * POST /api/symbology
   */
  async createSymbology(data: SymbologyCreate): Promise<SymbologyResponse> {
    try {
      console.log('Enviando dados para /api/symbology:', data);
      const response = await this.client.post<SymbologyResponse>(
        '/api/symbology',
        data
      );
      return response.data;
    } catch (error: any) {
      console.error('Erro ao criar simbologia:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Obter configuração completa de uma simbologia
   * GET /api/result/{url_key}/json
   */
  async getSymbologyConfig(urlKey: string): Promise<ConfigResponse> {
    const response = await this.client.get<ConfigResponse>(
      `/api/result/${urlKey}/json`
    );
    return response.data;
  }

  /**
   * Gerar URL de preview PNG
   * GET /api/result/{url_key}/png?size={size}
   */
  getPreviewUrl(urlKey: string, size: number = 200): string {
    return `/api/result/${urlKey}/png?size=${size}`;
  }

  /**
   * Gerar URL de SLD
   * GET /api/result/{url_key}/sld?layer_name={layer_name}
   */
  getSldUrl(urlKey: string, layerName: string = 'layer'): string {
    return `/api/result/${urlKey}/sld?layer_name=${layerName}`;
  }

  /**
   * Gerar URL de CSS
   * GET /api/result/{url_key}/css
   */
  getCssUrl(urlKey: string): string {
    return `/api/result/${urlKey}/css`;
  }

  /**
   * Gerar URL de REST payload
   * GET /api/result/{url_key}/rest
   */
  getRestUrl(urlKey: string): string {
    return `/api/result/${urlKey}/rest`;
  }

  /**
   * Buscar conteúdo SLD completo
   */
  async getSld(urlKey: string, layerName: string = 'layer'): Promise<string> {
    const response = await this.client.get(
      `/api/result/${urlKey}/sld?layer_name=${layerName}`,
      { responseType: 'text' }
    );
    return response.data;
  }

  /**
   * Buscar conteúdo CSS completo
   */
  async getCss(urlKey: string): Promise<string> {
    const response = await this.client.get(
      `/api/result/${urlKey}/css`,
      { responseType: 'text' }
    );
    return response.data;
  }

  /**
   * Buscar payload REST completo
   */
  async getRest(urlKey: string): Promise<string> {
    const response = await this.client.get(
      `/api/result/${urlKey}/rest`
    );
    return JSON.stringify(response.data, null, 2);
  }
}

export const api = new SymbologyAPI();
