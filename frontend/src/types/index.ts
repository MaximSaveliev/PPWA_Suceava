export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  current_plan?: string;
  operations_used?: number;
  operations_remaining?: number;
}

export interface Plan {
  id: number;
  name: string;
  max_operations: number;
  price: number;
  description: string;
  created_at: string;
  is_deleted?: boolean;
  deleted_at?: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  plan_id: number;
  operations_used: number;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  plan_name?: string;
  max_operations?: number;
  operations_remaining?: number;
}

export interface ImageRecord {
  id: number;
  user_id: number;
  filename: string;
  operation: string;
  original_size?: string;
  processed_size?: string;
  created_at: string;
  image_data?: string;
}

export type ImageOperation = 'crop' | 'grayscale' | 'sepia' | 'resize' | 'rotate' | 'blur';
