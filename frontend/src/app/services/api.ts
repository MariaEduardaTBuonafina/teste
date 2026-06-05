import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Lancamento {
  id?: number;
  descricao: string;
  valor: number;
  tipo: 'receita' | 'gasto';
  categoria: string;
  data?: string;
  mes?: string;
}

export interface Resumo {
  saldo_atual: number;
  total_receitas: number;
  total_gastos: number;
  receitas_mes: number;
  gastos_mes: number;
  saldo_mes: number;
}

export interface Relatorio {
  mes: string;
  receitas: number;
  gastos: number;
  saldo: number;
  maior_gasto: {
    descricao: string;
    valor: number;
  } | null;
}

@Injectable({
  providedIn: 'root'
})
export class Api {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  listarLancamentos(): Observable<Lancamento[]> {
    return this.http.get<Lancamento[]>(`${this.apiUrl}/lancamentos`);
  }

  adicionarLancamento(lancamento: Lancamento): Observable<Lancamento> {
    return this.http.post<Lancamento>(`${this.apiUrl}/lancamentos`, lancamento);
  }

  excluirLancamento(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/lancamentos/${id}`);
  }

  excluirTodos(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/lancamentos`);
  }

  buscarResumo(): Observable<Resumo> {
    return this.http.get<Resumo>(`${this.apiUrl}/resumo`);
  }

  buscarRelatorios(): Observable<Relatorio[]> {
    return this.http.get<Relatorio[]>(`${this.apiUrl}/relatorios`);
  }
}