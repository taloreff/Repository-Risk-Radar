export const demoScan = {
  repo: {
    owner: 'demo',
    name: 'vulnerable-webapp',
    full_name: 'demo/vulnerable-webapp',
    html_url: 'https://github.com/demo/vulnerable-webapp',
    default_branch: 'main',
    description: 'Representative dependency security scan fixture.'
  },
  scanned_ref: 'main',
  manifests: ['package.json', 'package-lock.json', 'requirements.txt'],
  dependencies: [
    {
      name: 'postcss',
      ecosystem: 'npm',
      source_file: 'package-lock.json',
      version_constraint: '^8.4.31',
      resolved_version: '8.4.31',
      dependency_type: 'direct'
    },
    {
      name: 'minimist',
      ecosystem: 'npm',
      source_file: 'package-lock.json',
      resolved_version: '0.0.8',
      dependency_type: 'direct'
    },
    {
      name: 'requests',
      ecosystem: 'PyPI',
      source_file: 'requirements.txt',
      version_constraint: '>=2.0',
      resolved_version: null,
      dependency_type: 'direct'
    }
  ],
  findings: [
    {
      dependency: {
        name: 'minimist',
        ecosystem: 'npm',
        source_file: 'package-lock.json',
        resolved_version: '0.0.8',
        dependency_type: 'direct'
      },
      vulnerability: {
        id: 'GHSA-xvch-5gv4-984h',
        summary: 'Prototype pollution in minimist.',
        aliases: ['CVE-2021-44906'],
        fixed_versions: ['1.2.6'],
        references: [{ type: 'ADVISORY', url: 'https://github.com/advisories/GHSA-xvch-5gv4-984h' }]
      },
      cves: [
        {
          cve_id: 'CVE-2021-44906',
          cvss_score: 9.8,
          severity: 'CRITICAL',
          epss_score: 0.0324,
          epss_percentile: 0.871,
          epss_date: '2026-06-01',
          cwe_ids: ['CWE-1321'],
          cisa_known_exploited: false,
          cisa_due_date: null,
          published: '2022-03-18T00:00:00.000',
          last_modified: '2025-11-21T00:00:00.000',
          references: ['https://nvd.nist.gov/vuln/detail/CVE-2021-44906']
        }
      ],
      risk_score: 99.2,
      risk_level: 'critical',
      reasons: [
        'CRITICAL severity adds 40 points.',
        'CVSS 9.8 adds 39.2 points.',
        'EPSS 0.032 adds 5 exploit-likelihood points.',
        'Direct dependency adds 10 points.',
        'A fixed version is known, lowering remediation uncertainty.'
      ],
      fix_available: true,
      fixed_versions: ['1.2.6']
    },
    {
      dependency: {
        name: 'postcss',
        ecosystem: 'npm',
        source_file: 'package-lock.json',
        resolved_version: '8.4.31',
        dependency_type: 'direct'
      },
      vulnerability: {
        id: 'GHSA-qx2v-qp2m-jg93',
        summary: 'PostCSS has XSS via unescaped style output.',
        aliases: ['CVE-2026-0001'],
        fixed_versions: ['8.5.10'],
        references: [{ type: 'ADVISORY', url: 'https://github.com/advisories/GHSA-qx2v-qp2m-jg93' }]
      },
      cves: [
        {
          cve_id: 'CVE-2026-0001',
          cvss_score: 5.3,
          severity: 'MEDIUM',
          epss_score: 0.004,
          epss_percentile: 0.41,
          epss_date: '2026-06-01',
          cwe_ids: ['CWE-79'],
          cisa_known_exploited: false,
          cisa_due_date: null,
          published: '2026-05-20T00:00:00.000',
          last_modified: '2026-05-22T00:00:00.000',
          references: ['https://github.com/advisories/GHSA-qx2v-qp2m-jg93']
        }
      ],
      risk_score: 56.4,
      risk_level: 'medium',
      reasons: [
        'MEDIUM severity adds 18 points.',
        'CVSS 5.3 adds 21.2 points.',
        'Direct dependency adds 10 points.',
        'A fixed version is known, lowering remediation uncertainty.'
      ],
      fix_available: true,
      fixed_versions: ['8.5.10']
    }
  ],
  stats: {
    dependencies_with_resolved_versions: 2,
    dependencies_without_resolved_versions: 1,
    osv_queries: 2,
    osv_vulnerabilities: 2,
    cves_enriched: 2,
    epss_enriched: 2
  },
  narrative: {
    executive_summary:
      'The demo scan found two dependency vulnerabilities, including one critical minimist advisory with a known fixed version.',
    technical_summary:
      'OSV matched exact dependency versions, NVD supplied CVSS and CWE context, and EPSS added exploitation likelihood signals.',
    remediation_plan: [
      'Update minimist to 1.2.6 or later and run the package test suite.',
      'Update postcss to 8.5.10 or later and rebuild frontend assets.',
      'Commit lockfiles so every production dependency can be checked exactly.'
    ],
    questions: ['Are dev dependencies bundled into production assets?'],
    ai_generated: false
  },
  release_gate: {
    decision: 'BLOCK',
    confidence: 'high',
    risk_score: 99.2,
    blocking_reasons: [
      'Critical direct dependency has a known fixed version.',
      'Direct dependency has CVSS >= 9.0.',
      'Overall risk score is 99.2, meeting the BLOCK threshold.'
    ],
    warning_reasons: [],
    required_actions: [
      'Upgrade minimist from 0.0.8 to at least 1.2.6, regenerate lockfiles, and run tests.',
      'Upgrade postcss from 8.4.31 to at least 8.5.10, regenerate lockfiles, and run tests.',
      'Re-run Repo Risk Radar and verify the release gate no longer returns BLOCK.'
    ],
    evidence: [
      'minimist@0.0.8 (direct) -> GHSA-xvch-5gv4-984h; CVEs: CVE-2021-44906; CVSS: 9.8; fix: 1.2.6; risk: 99.2'
    ],
    unknowns: ['1 dependencies were skipped because exact versions were unavailable.'],
    pass_conditions: [
      'No known exploited dependency findings remain.',
      'No direct dependency has critical severity with a known fix still unapplied.',
      'No direct dependency finding has CVSS >= 9.0.',
      'Overall release gate risk score is below 50.',
      'Resolve unpinned dependencies so OSV can match exact deployed versions.'
    ],
    developer_ticket: {
      title: '[BLOCK] Dependency security release gate for demo/vulnerable-webapp',
      description:
        'Repo Risk Radar release gate returned BLOCK for demo/vulnerable-webapp with risk score 99.2.\n\nPolicy reasons:\n- Critical direct dependency has a known fixed version.\n- Direct dependency has CVSS >= 9.0.\n- Overall risk score is 99.2, meeting the BLOCK threshold.\n\nAffected packages:\n- minimist\n- postcss\n\nCVEs:\n- CVE-2021-44906\n- CVE-2026-0001\n\nRequired actions:\n- Upgrade minimist from 0.0.8 to at least 1.2.6, regenerate lockfiles, and run tests.\n- Upgrade postcss from 8.4.31 to at least 8.5.10, regenerate lockfiles, and run tests.\n- Re-run Repo Risk Radar and verify the release gate no longer returns BLOCK.',
      acceptance_criteria: [
        'Vulnerable direct dependencies are upgraded to non-vulnerable versions where fixes are available.',
        'Lockfiles are regenerated and committed.',
        'Project tests pass.',
        'Repo Risk Radar re-scan no longer returns BLOCK for unresolved dependency risk.',
        'Any remaining risk is documented and accepted by the release owner.'
      ],
      evidence: [
        'minimist@0.0.8 (direct) -> GHSA-xvch-5gv4-984h; CVEs: CVE-2021-44906; CVSS: 9.8; fix: 1.2.6; risk: 99.2'
      ]
    },
    explanation: {
      executive_summary:
        'demo/vulnerable-webapp should not be released to production until dependency security blocking items are remediated.',
      technical_summary:
        'Release gate evaluated 2 findings, 3 dependencies, and 3 manifests. The computed release risk score is 99.2.',
      release_decision_explanation:
        'The deterministic policy returned BLOCK because at least one blocking threshold fired.',
      top_required_actions: [
        'Upgrade minimist from 0.0.8 to at least 1.2.6, regenerate lockfiles, and run tests.',
        'Upgrade postcss from 8.4.31 to at least 8.5.10, regenerate lockfiles, and run tests.',
        'Re-run Repo Risk Radar and verify the release gate no longer returns BLOCK.'
      ],
      safe_fix_plan: [
        'Upgrade minimist from 0.0.8 to at least 1.2.6, regenerate lockfiles, and run tests.',
        'Upgrade postcss from 8.4.31 to at least 8.5.10, regenerate lockfiles, and run tests.'
      ],
      what_would_make_this_pass: [
        'No known exploited dependency findings remain.',
        'No direct dependency has critical severity with a known fix still unapplied.',
        'No direct dependency finding has CVSS >= 9.0.',
        'Overall release gate risk score is below 50.'
      ],
      developer_ticket: {
        title: '[BLOCK] Dependency security release gate for demo/vulnerable-webapp',
        description:
          'Repo Risk Radar release gate returned BLOCK for demo/vulnerable-webapp with risk score 99.2.\n\nRequired actions:\n- Upgrade minimist from 0.0.8 to at least 1.2.6, regenerate lockfiles, and run tests.\n- Upgrade postcss from 8.4.31 to at least 8.5.10, regenerate lockfiles, and run tests.',
        acceptance_criteria: [
          'Vulnerable direct dependencies are upgraded to non-vulnerable versions where fixes are available.',
          'Lockfiles are regenerated and committed.',
          'Project tests pass.',
          'Repo Risk Radar re-scan no longer returns BLOCK.'
        ],
        evidence: [
          'minimist@0.0.8 (direct) -> GHSA-xvch-5gv4-984h; CVEs: CVE-2021-44906; CVSS: 9.8; fix: 1.2.6; risk: 99.2'
        ]
      },
      questions_for_developer: ['Is requests resolved and deployed in production?'],
      ai_generated: false
    }
  },
  generated_at: new Date().toISOString()
};
