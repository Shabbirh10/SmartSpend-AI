'use client';

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  perPage: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  perPage,
  onPageChange,
  className = '',
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const startItem = (currentPage - 1) * perPage + 1;
  const endItem = Math.min(currentPage * perPage, totalItems);

  const getPageNumbers = (): (number | '...')[] => {
    const pages: (number | '...')[] = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible + 2) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 font-mono uppercase text-xs tracking-widest ${className}`}>
      <p className="text-[#003049] font-bold">
        Records <span className="text-[#c1121f]">{startItem}</span>-<span className="text-[#c1121f]">{endItem}</span> / {totalItems}
      </p>

      <nav className="flex items-center gap-2" aria-label="Pagination">
        <button
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1}
          className="p-1.5 border-2 border-[#003049] text-[#003049] hover:bg-[#003049] hover:text-white disabled:opacity-30 disabled:hover:bg-transparent transition-colors shadow-[2px_2px_0px_0px_#003049]"
        >
          <ChevronsLeft size={16} />
        </button>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="p-1.5 border-2 border-[#003049] text-[#003049] hover:bg-[#003049] hover:text-white disabled:opacity-30 disabled:hover:bg-transparent transition-colors shadow-[2px_2px_0px_0px_#003049]"
        >
          <ChevronLeft size={16} />
        </button>

        <div className="flex items-center gap-2 mx-2">
          {pageNumbers.map((page, index) =>
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="w-8 h-8 flex items-center justify-center text-[#669bbc] font-bold">
                ···
              </span>
            ) : (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={`w-8 h-8 flex items-center justify-center border-2 border-[#003049] font-bold transition-all ${
                  currentPage === page
                    ? 'bg-[#c1121f] text-white shadow-[2px_2px_0px_0px_#003049]'
                    : 'bg-white text-[#003049] hover:bg-[#003049] hover:text-white shadow-[2px_2px_0px_0px_#003049]'
                }`}
              >
                {page}
              </button>
            )
          )}
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="p-1.5 border-2 border-[#003049] text-[#003049] hover:bg-[#003049] hover:text-white disabled:opacity-30 disabled:hover:bg-transparent transition-colors shadow-[2px_2px_0px_0px_#003049]"
        >
          <ChevronRight size={16} />
        </button>
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages}
          className="p-1.5 border-2 border-[#003049] text-[#003049] hover:bg-[#003049] hover:text-white disabled:opacity-30 disabled:hover:bg-transparent transition-colors shadow-[2px_2px_0px_0px_#003049]"
        >
          <ChevronsRight size={16} />
        </button>
      </nav>
    </div>
  );
}
