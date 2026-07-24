const nodes = [
  ['01', 'CODE', 'Read the product'],
  ['02', 'DEMAND', 'Find real searches'],
  ['03', 'SHIP', 'Create and publish'],
  ['04', 'SIGNAL', 'Collect outcomes'],
  ['05', 'MEMORY', 'Choose what follows'],
];

export function GrowthTrace() {
  return (
    <div className="growth-trace" aria-label="Growth Lab loop from code to market">
      <div className="trace-beam" aria-hidden="true"><span /></div>
      {nodes.map(([number, label, detail]) => (
        <div className="trace-node" key={number}>
          <span className="trace-index">{number}</span>
          <strong>{label}</strong>
          <small>{detail}</small>
        </div>
      ))}
      <div className="trace-return">
        <span>market evidence returns to the next decision</span>
        <span aria-hidden="true">↩</span>
      </div>
    </div>
  );
}
