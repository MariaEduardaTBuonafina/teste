import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Api, Lancamento, Resumo } from '../../services/api';

@Component({
  selector: 'app-home',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  lancamentos: Lancamento[] = [];

  resumo: Resumo = {
    saldo_atual: 0,
    total_receitas: 0,
    total_gastos: 0,
    receitas_mes: 0,
    gastos_mes: 0,
    saldo_mes: 0
  };

  descricao = '';
  valor: number | null = null;
  tipoAtual: 'receita' | 'gasto' = 'receita';
  categoria = 'Alimentação';

  feedback = '';
  feedbackTipo: 'sucesso' | 'erro' | '' = '';

  categorias = [
    'Alimentação',
    'Transporte',
    'Moradia',
    'Saúde',
    'Educação',
    'Lazer',
    'Outros'
  ];

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.carregarTudo();
  }

  selecionarTipo(tipo: 'receita' | 'gasto'): void {
    this.tipoAtual = tipo;
  }

  adicionarLancamento(): void {
    if (!this.descricao.trim()) {
      this.mostrarFeedback('⚠️ Preencha a descrição!', 'erro');
      return;
    }

    if (!this.valor || this.valor <= 0) {
      this.mostrarFeedback('⚠️ Informe um valor válido!', 'erro');
      return;
    }

    const novoLancamento: Lancamento = {
      descricao: this.descricao.trim(),
      valor: this.valor,
      tipo: this.tipoAtual,
      categoria: this.categoria
    };

    this.api.adicionarLancamento(novoLancamento).subscribe({
      next: () => {
        this.descricao = '';
        this.valor = null;
        this.mostrarFeedback('✅ Lançamento adicionado com sucesso!', 'sucesso');
        this.carregarTudo();
      },
      error: () => {
        this.mostrarFeedback('❌ Erro ao conectar com o servidor.', 'erro');
      }
    });
  }

  excluirLancamento(id?: number): void {
    if (!id) return;

    const confirmar = confirm('Tem certeza que deseja excluir este lançamento?');

    if (!confirmar) return;

    this.api.excluirLancamento(id).subscribe({
      next: () => {
        this.carregarTudo();
      },
      error: () => {
        alert('Erro ao excluir. Verifique se o servidor está rodando.');
      }
    });
  }

  apagarTodos(): void {
    const confirmar = confirm('Tem certeza que deseja apagar TODOS os lançamentos?');

    if (!confirmar) return;

    this.api.excluirTodos().subscribe({
      next: () => {
        this.mostrarFeedback('🗑️ Todos os lançamentos foram removidos!', 'sucesso');
        this.carregarTudo();
      },
      error: () => {
        this.mostrarFeedback('❌ Erro ao apagar os lançamentos.', 'erro');
      }
    });
  }

  carregarTudo(): void {
    this.api.listarLancamentos().subscribe({
      next: (dados) => {
        this.lancamentos = [...dados].reverse();
      },
      error: () => {
        console.error('Erro ao carregar lançamentos');
      }
    });

    this.api.buscarResumo().subscribe({
      next: (dados) => {
        this.resumo = dados;
      },
      error: () => {
        console.error('Erro ao carregar resumo');
      }
    });
  }

  formatarReais(valor: number): string {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  }

  mostrarFeedback(mensagem: string, tipo: 'sucesso' | 'erro'): void {
    this.feedback = mensagem;
    this.feedbackTipo = tipo;

    setTimeout(() => {
      this.feedback = '';
      this.feedbackTipo = '';
    }, 3000);
  }
}