import { Pipe, PipeTransform } from '@angular/core';

/**
 * Pipe de formatage monétaire en Ariary Malgache (Ar).
 * Usage : {{ value | currencyMga }} → "1 500 000 Ar"
 */
@Pipe({
  name: 'currencyMga',
  standalone: true,
})
export class CurrencyMgaPipe implements PipeTransform {
  transform(value: string | number | null | undefined): string {
    if (value === null || value === undefined || value === '') {
      return '— Ar';
    }

    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) {
      return '— Ar';
    }

    // Formatage avec séparateur de milliers (espace) et 2 décimales
    const formatted = num.toLocaleString('fr-FR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    return `${formatted} Ar`;
  }
}
