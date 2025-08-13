import React from 'react';

interface Policy {
  id: number;
  insurer: string;
  product_type: string;
  premium_monthly: number;
  deductible: number;
  coverage_limit: number;
  owner_name: string;
  policy_number: string;
  start_date: string;
  end_date: string;
  notes?: string;
  active: boolean;
  user_id: string;
  pdf_file_path?: string;
  pdf_file_size?: number;
  original_filename?: string;
  policy_language?: string;
  coverage_details?: string;
  terms_and_conditions?: string;
  extraction_confidence?: number;
}

interface PolicyRowProps {
  policy: Policy;
  isSelected: boolean;
  onSelect: (id: number) => void;
  onViewPdf: (policyId: number, filename: string) => void;
  onEdit: (policy: Policy) => Promise<void>;
  onDelete: (id: number) => void;
}

const PolicyRow: React.FC<PolicyRowProps> = ({
  policy,
  isSelected,
  onSelect,
  onViewPdf,
  onEdit,
  onDelete
}) => {
  const isHebrew = policy.policy_language === 'he';
  
  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getLanguageFlag = () => {
    switch (policy.policy_language) {
      case 'he': return '🇮🇱';
      case 'en': return '🇺🇸';
      default: return '🌐';
    }
  };

  const getConfidenceBadge = () => {
    if (!policy.extraction_confidence) return null;
    const confidence = policy.extraction_confidence;
    let badgeClass = 'confidence-badge ';
    
    if (confidence >= 0.8) badgeClass += 'high';
    else if (confidence >= 0.6) badgeClass += 'medium';
    else badgeClass += 'low';

    return (
      <span className={badgeClass} title={`Extraction confidence: ${Math.round(confidence * 100)}%`}>
        {Math.round(confidence * 100)}%
      </span>
    );
  };

  return (
    <tr 
      className={`policy-row ${isSelected ? 'selected' : ''}`}
    >
      <td className="checkbox-cell">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onSelect(policy.id)}
          className="policy-checkbox"
        />
      </td>
      
      <td className="policy-name-cell">
        <div className="policy-name-container">
          <span 
            className="policy-name" 
            title={policy.policy_number}
            style={{ direction: isHebrew ? 'rtl' : 'ltr', textAlign: isHebrew ? 'right' : 'left' }}
          >
            {policy.policy_number}
          </span>
          <div className="policy-meta">
            <span className="language-flag">{getLanguageFlag()}</span>
            {getConfidenceBadge()}
          </div>
        </div>
      </td>
      
      <td className="insurer-cell">
        <span 
          className="insurer-name"
          style={{ direction: isHebrew ? 'rtl' : 'ltr', textAlign: isHebrew ? 'right' : 'left' }}
        >
          {policy.insurer}
        </span>
      </td>
      
      <td className="type-cell">
        <span className={`type-badge type-${policy.product_type.toLowerCase().replace(/\s+/g, '-')}`}>
          {policy.product_type}
        </span>
      </td>
      
      <td className="owners-cell">
        <span 
          className="owners-text" 
          title={policy.owner_name}
          style={{ direction: isHebrew ? 'rtl' : 'ltr', textAlign: isHebrew ? 'right' : 'left' }}
        >
          {policy.owner_name}
        </span>
      </td>
      
      <td className="dates-cell">
        <div className="date-range">
          <div className="date-item">
            <span className="date-label">Start:</span>
            <span className="date-value">{formatDate(policy.start_date)}</span>
          </div>
          <div className="date-item">
            <span className="date-label">End:</span>
            <span className="date-value">{formatDate(policy.end_date)}</span>
          </div>
        </div>
      </td>
      
      <td className="premium-cell">
        <div className="premium-info">
          <div className="premium-monthly">
            {formatCurrency(policy.premium_monthly)}/mo
          </div>
          <div className="deductible">
            Deductible: {formatCurrency(policy.deductible)}
          </div>
        </div>
      </td>
      
      <td className="id-cell">
        <span className="policy-id">#{policy.id}</span>
      </td>
      
      <td className="actions-cell">
        <div className="action-buttons">
          <button
            className="btn btn-sm btn-outline-primary"
            onClick={() => onViewPdf(policy.id, policy.original_filename || 'policy.pdf')}
            title="View PDF"
          >
            📄
          </button>
          
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => onEdit(policy)}
            title="Edit Policy"
          >
            ✏️
          </button>
          
          <button
            className="btn btn-sm btn-outline-danger"
            onClick={() => {
              if (confirm(`Are you sure you want to delete policy "${policy.policy_number}"?`)) {
                onDelete(policy.id);
              }
            }}
            title="Delete Policy"
          >
            🗑️
          </button>
        </div>
      </td>
    </tr>
  );
};

export default PolicyRow;
