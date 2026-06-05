import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Api, Relatorio } from '../../services/api';

@Component({
  selector: 'app-relatorios',
  imports: [CommonModule, RouterLink],
  templateUrl: './relatorios.html',
  styleUrl: './relatorios.css'
})
export class Relatorios implements OnInit {
  relatorios: Relatorio[] = [];
  carregando = true;
  erro = '';

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.carregarRelatorios();
  }

  carregarRelatorios(): void {
    this.carregando = true;
    this.erro = '';

    this.api.buscarRelatorios().subscribe({
      next: (dados) => {
        this.relatorios = dados;
        this.carregando = false;
      },
      error: () => {
        this.erro = 'Erro ao carregar relatórios. Verifique se o backend está rodando.';
        this.carregando = false;
      }
    });
  }

  formatarReais(valor: number): string {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  }
}