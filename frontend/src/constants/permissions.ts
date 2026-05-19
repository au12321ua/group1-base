export const PERM = {
  USER_READ: "user:read",
  USER_CREATE: "user:create",
  COURSE_READ: "course:read",
  OFFERING_READ: "offering:read",
  SCHEDULE_READ: "schedule:read",
  CALENDAR_READ: "calendar:read",
  TRAINING_READ: "training:read",
  BASE_INFO_READ: "base-info:read",
  RECYCLE_READ: "recycle:read",
  AUDIT_READ: "audit:read",
} as const;

export type PermissionCode = (typeof PERM)[keyof typeof PERM];
