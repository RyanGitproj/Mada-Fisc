/**
 * Modèles de réponse API standardisés.
 */

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiErrorResponse {
  error: ApiError;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DashboardSummary {
  periode: {
    mois: number;
    annee: number;
  };
  payroll: {
    masse_salariale_brute: string;
    masse_salariale_nette: string;
    total_irsa: string;
    nombre_bulletins: number;
    employes_actifs: number;
  };
  invoicing: {
    tva_collectee: string;
    factures_en_attente: {
      nombre: number;
      montant_ht: string;
    };
    factures_en_retard: {
      nombre: number;
      montant_ht: string;
    };
  };
  derniers_bulletins: Array<{
    id: number;
    employee_name: string;
    month: number;
    year: number;
    net_salary: string;
    generated_at: string;
  }>;
}

export interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  base_salary: string;
  hire_date: string;
  birth_date: string | null;
  dependants_count: number;
  cnaps_number: string;
  organism_sanitaire: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Payslip {
  id: number;
  employee: number;
  employee_name: string;
  employee_email: string;
  month: number;
  year: number;
  gross_salary: string;
  cnaps_deduction: string;
  ostie_deduction: string;
  fmfp_deduction: string;
  irsa_tax: string;
  net_salary: string;
  dependants_count: number;
  is_paid: boolean;
  paid_at: string | null;
  generated_at: string;
}

export interface Client {
  id: number;
  company_name: string;
  nif: string;
  stat: string;
  email: string;
  phone: string;
  address: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  client: number;
  client_name: string;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  amount_ht: string;
  tva_amount: string;
  amount_ttc: string;
  status: 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE';
  is_overdue: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface PayslipGenerateRequest {
  employee_id: number;
  month: number;
  year: number;
}

export interface PayslipGenerateResponse {
  message: string;
  data: {
    gross_salary: string;
    cnaps_deduction: string;
    ostie_deduction: string;
    fmfp_deduction: string;
    base_irsa: string;
    irsa_tax: string;
    net_salary: string;
    dependants_count: number;
  };
}

export interface InvoiceCreateRequest {
  client_id: number;
  amount_ht: string;
  due_date: string;
  issue_date?: string;
  notes?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    is_staff: boolean;
  };
}

export interface MonthlySummary {
  total_gross: string;
  total_cnaps: string;
  total_ostie: string;
  total_fmfp: string;
  total_irsa: string;
  total_net: string;
  count: number;
}
