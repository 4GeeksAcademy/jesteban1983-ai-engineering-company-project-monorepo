# Skill: Añadir sección de página

**Objetivo:** Insertar una nueva sección funcional en el website o backoffice siguiendo la arquitectura actual.

**Inputs:**
- `targetFile`: Archivo donde se insertará (ej. `page.tsx`).
- `sectionTitle`: Título visible de la sección.
- `content`: Componente o estructura de la sección.

**Pasos:**
1. Verificar que el componente no duplica lógica existente.
2. Crear el componente en `uis/website/components/`.
3. Importarlo en `page.tsx`.
4. Ejecutar `npm run type-check`.

**Criterios de Aceptación:**
- El componente no contiene estilos en línea (Regla `.agents/rules/no-inline-styles.md`).
- El componente está tipado con TypeScript.
- `npm run type-check` pasa sin errores.