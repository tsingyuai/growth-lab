const nodesEn = [
  ['01', 'CODE', 'Read the product'],
  ['02', 'DEMAND', 'Find real searches'],
  ['03', 'SHIP', 'Create and publish'],
  ['04', 'SIGNAL', 'Collect outcomes'],
  ['05', 'MEMORY', 'Choose what follows'],
];

const nodesZh = [
  ['01', '代码', '理解产品'],
  ['02', '需求', '发现真实搜索'],
  ['03', '执行', '创作并发布'],
  ['04', '信号', '采集结果'],
  ['05', '记忆', '决定下一步'],
];

export function GrowthTrace({ locale = 'en' }: { locale?: 'en' | 'zh' }) {
  const nodes = locale === 'zh' ? nodesZh : nodesEn;
  return (
    <div className="growth-trace" aria-label={locale === 'zh' ? 'Growth Lab 从代码到市场的闭环' : 'Growth Lab loop from code to market'}>
      <div className="trace-beam" aria-hidden="true"><span /></div>
      {nodes.map(([number, label, detail]) => (
        <div className="trace-node" key={number}>
          <span className="trace-index">{number}</span>
          <strong>{label}</strong>
          <small>{detail}</small>
        </div>
      ))}
      <div className="trace-return">
        <span>{locale === 'zh' ? '市场证据进入下一次决策' : 'market evidence returns to the next decision'}</span>
        <span aria-hidden="true">↩</span>
      </div>
    </div>
  );
}
