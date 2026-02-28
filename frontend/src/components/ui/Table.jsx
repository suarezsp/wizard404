/**
 * Table.jsx - Tabla reutilizable estilo 16-bit.
 * columnas: [{ key, label }]. data: array de objetos. Cabecera y filas con bordes y colores.
 */
export function Table({ columns, data, emptyMessage = 'Sin datos.', renderCell, staggerRows, onRowClick }) {
  return (
    <div className={`border-2 border-[var(--pixel-border)] overflow-x-auto ${staggerRows ? 'table-rows-stagger' : ''}`}>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b-2 border-[var(--pixel-border)] bg-[#1a1a2e]">
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left p-3 text-[var(--pixel-accent)]"
                style={col.align === 'right' ? { textAlign: 'right' } : undefined}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr
              key={row.id ?? i}
              role={onRowClick ? 'button' : undefined}
              tabIndex={onRowClick ? 0 : undefined}
              onClick={onRowClick ? () => onRowClick(row, i) : undefined}
              onKeyDown={onRowClick ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onRowClick(row, i) } } : undefined}
              className={`border-b border-[var(--pixel-border)] hover:bg-[#1a1a2e] ${onRowClick ? 'cursor-pointer' : ''}`}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className="p-3 text-[var(--pixel-text)]"
                  style={col.align === 'right' ? { textAlign: 'right' } : undefined}
                >
                  {renderCell
                    ? renderCell(col.key, row[col.key], row)
                    : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <p className="p-6 text-center text-[var(--pixel-muted)]">
          {emptyMessage}
        </p>
      )}
    </div>
  )
}
